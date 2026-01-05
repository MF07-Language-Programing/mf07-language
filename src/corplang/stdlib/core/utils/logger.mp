"""Structured, runtime-aware logger for the consolidated core."""

from core.system.runtime_info import RuntimeInfo
from core.system.datetime_wrapper import DateTime


class LogLevel {
	static var DEBUG: int = 10
	static var INFO: int = 20
	static var WARNING: int = 30
	static var ERROR: int = 40
	static var CRITICAL: int = 50

	static intent name(level: int): string {
		if (level == LogLevel.DEBUG) { return "DEBUG" }
		if (level == LogLevel.INFO) { return "INFO" }
		if (level == LogLevel.WARNING) { return "WARNING" }
		if (level == LogLevel.ERROR) { return "ERROR" }
		if (level == LogLevel.CRITICAL) { return "CRITICAL" }
		return "LEVEL-" + level
	}

	static intent normalize(levelValue): int {
		if (levelValue == null) {
			return LogLevel.INFO
		}

		var valueType = type(levelValue)
		if (valueType == "int") {
			return levelValue
		}

		if (valueType == "string" or valueType == "str") {
			if (levelValue == "debug" or levelValue == "DEBUG" or levelValue == "Debug") { return LogLevel.DEBUG }
			if (levelValue == "info" or levelValue == "INFO" or levelValue == "Info") { return LogLevel.INFO }
			if (levelValue == "warning" or levelValue == "WARNING" or levelValue == "Warning" or levelValue == "warn" or levelValue == "WARN") { return LogLevel.WARNING }
			if (levelValue == "error" or levelValue == "ERROR" or levelValue == "Error") { return LogLevel.ERROR }
			if (levelValue == "critical" or levelValue == "CRITICAL" or levelValue == "Critical" or levelValue == "fatal" or levelValue == "FATAL") { return LogLevel.CRITICAL }
		}

		return LogLevel.INFO
	}

	static intent is_enabled(level: int, threshold: int): bool {
		return level >= threshold
	}
}


class LogRecord {
	var level: int
	var levelName: string
	var message: string
	var timestamp: any
	var loggerName: string
	var context: any
	var error: any
	var callsite: string
	var emitterModule: string

	intent constructor(level: int, message: string, loggerName: string, context: any, err: any, callsite: string, emitterModule: string) {
		this.level = level
		this.levelName = LogLevel.name(level)
		this.message = message
		this.loggerName = loggerName
		this.context = context
		this.error = err
		try {
			this.timestamp = DateTime.now()
		} catch (e: Exception) {
			this.timestamp = null
		}
		this.callsite = callsite
		this.emitterModule = emitterModule
	}
}


class LogFormatter {
	private var color: bool

	intent constructor(color: Optional[bool] = false) {
		this.color = color == null ? false : color
	}

	intent _get_color_code(level: int): string {
		if (not this.color) {
			return ""
		}
		/* ANSI color codes */
		if (level == LogLevel.DEBUG) { return "\u001b[36m" }      /* Cyan */
		if (level == LogLevel.INFO) { return "\u001b[32m" }       /* Green */
		if (level == LogLevel.WARNING) { return "\u001b[33m" }    /* Yellow */
		if (level == LogLevel.ERROR) { return "\u001b[31m" }      /* Red */
		if (level == LogLevel.CRITICAL) { return "\u001b[35m" }   /* Magenta */
		return ""
	}

	intent _get_reset_code(): string {
		return this.color ? "\u001b[0m" : ""
	}

	intent _get_level_name(level: int): string {
		if (level == LogLevel.DEBUG) { return "DEBUG" }
		if (level == LogLevel.INFO) { return "INFO" }
		if (level == LogLevel.WARNING) { return "WARNING" }
		if (level == LogLevel.ERROR) { return "ERROR" }
		if (level == LogLevel.CRITICAL) { return "CRITICAL" }
		return "LOG"
	}

	intent _format_timestamp_ms(record): string {
		try {
			if (record.timestamp == null) {
				return "0000-00-00 00:00:00.000"
			}
			var ts_with_ms = mf.datetime.format_ms(record.timestamp._native_dt, "%Y-%m-%d %H:%M:%S.%ms")
			if (ts_with_ms == null or ts_with_ms == "") {
				return "0000-00-00 00:00:00.000"
			}
			return ts_with_ms
		} catch (e: Exception) {
			return "0000-00-00 00:00:00.000"
		}
	}

	intent _format_location(record): string {
		var location = "";
		
		if (record.emitterModule != null and record.emitterModule != "") {
			location = record.emitterModule;
		} else {
			location = "core";
		}

		if (record.callsite != null and record.callsite != "") {
			location = f"{location}:{record.callsite}";
		} else {
			location = "{location}:unknown:0";
		}

		return location;
	}

	intent _format_context(ctx): string {
		if (ctx == null) {
			return ""
		}
		var keys = mf.objects.keys(ctx)
		if (len(keys) == 0) {
			return ""
		}

		var buffer = ""
		var i = 0
		while (i < len(keys)) {
			var k = keys[i]
			var v = null
			try {
				v = mf.objects.mapGet(ctx, k)
			} catch (e: Exception) {
				try { v = ctx[k] } catch (err: Exception) { v = null }
			}
			if (i > 0) {
				buffer = buffer + " "
			}
			buffer = buffer + f"{k}={v}"
			i = i + 1
		}
		return buffer
	}

	intent format(record: LogRecord): string {
		var timestamp = this._format_timestamp_ms(record);
		var level = this._get_level_name(record.level);
		var location = this._format_location(record);
		var message = record.message;
		var mainLine = f"{timestamp} | {level} | {location} - {message}";
		var color = this._get_color_code(record.level);
		var reset = this._get_reset_code();

		if (this.color) {
			mainLine = color + mainLine + reset;
		}

		var output = mainLine;
		var contextStr = this._format_context(record.context);
		
		if (contextStr != "") {
			output = output + "\n    " + contextStr;
		}

		if (record.error != null) {
			output = output + "\n    error=" + record.error;
		}

		return output;
	}

}


class ConsoleHandler {
	private var formatter: LogFormatter
	private var color: bool

	intent constructor(formatter: Optional[LogFormatter] = null, color: Optional[bool] = false) {
		this.color = color == null ? false : color
		this.formatter = formatter
		if (this.formatter == null) {
			this.formatter = new LogFormatter(this.color)
		}
	}

	intent emit(record: LogRecord) {
		try {
			var rendered = this.formatter.format(record)
			sout(rendered)
		} catch (e: Exception) {
			try {
				sout("Logger ConsoleHandler failure: " + e)
				sout("Fallback log: " + record.message)
			} catch (err: Exception) {
				/* terminal unavailable; swallow to keep runtime alive */
			}
		}
	}
}


class Logger {
	private var name: string
	private var level: int
	private var handlers
	private var hooks
	private var baseContext
	private var emitterModule
	private var color: bool

	intent constructor(name: Optional[string] = null, level: Optional[int] = null, handlersList: Optional[list] = null, context: Optional[dict] = null, color: Optional[bool] = false) {
		this.name = name == null ? "core" : name
		this.level = LogLevel.normalize(level)
		this.color = color == null ? false : color
		this.handlers = handlersList
		if (this.handlers == null) {
			this.handlers = []
		}
		if (len(this.handlers) == 0) {
			this.handlers.append(new ConsoleHandler(null, this.color))
		}
		this.hooks = []
		this.baseContext = context
		if (this.baseContext == null) {
			this.baseContext = {}
		}
		this.emitterModule = this.name
	}

	intent setLevel(levelValue) {
		this.level = LogLevel.normalize(levelValue)
	}

	intent addHandler(handler) {
		if (handler == null) {
			return
		}
		this.handlers.append(handler)
	}

	intent clearHandlers() {
		this.handlers = []
	}

	intent addHook(hookFn) {
		if (hookFn == null) {
			return
		}
		this.hooks.append(hookFn)
	}

	intent bindDriver(driverFn) {
		this.addHook(driverFn)
	}

	intent setModule(moduleName: string) {
		this.emitterModule = moduleName
	}

	intent setDriver(driverName: string) {
		try {
			mf.objects.mapPut(this.baseContext, "driver", driverName)
		} catch (e: Exception) {
			/* ignore if baseContext is not map-like */
		}
	}

	intent _merge_context(target, source) {
		if (source == null) {
			return
		}
		var keys = mf.objects.keys(source)
		var i = 0
		while (i < len(keys)) {
			var k = keys[i]
			var v = null
			try {
				v = mf.objects.mapGet(source, k)
			} catch (e: Exception) {
				try { v = source[k] } catch (err: Exception) { v = null }
			}
			mf.objects.mapPut(target, k, v)
			i = i + 1
		}
	}

	intent _build_context(extra) {
		var ctx = mf.objects.Map()
		mf.objects.mapPut(ctx, "runtime_vendor", RuntimeInfo.vendor())
		mf.objects.mapPut(ctx, "runtime_version", RuntimeInfo.version())
		mf.objects.mapPut(ctx, "runtime_mode", RuntimeInfo.mode())
		this._merge_context(ctx, this.baseContext)
		this._merge_context(ctx, extra)
		return ctx
	}

	intent _callsite(): string {
		try {
			return mf.runtime.callsite()
		} catch (e: Exception) {
			return ""
		}
	}

	intent _dispatch(record: LogRecord) {
		var i = 0
		while (i < len(this.handlers)) {
			var handler = this.handlers[i]
			try {
				handler.emit(record)
			} catch (e: Exception) {
				try {
					sout("Logger handler failure: " + e)
				} catch (err: Exception) {
					/* swallow secondary failure to keep runtime alive */
				}
			}
			i = i + 1
		}

		var h = 0
		while (h < len(this.hooks)) {
			var hookFn = this.hooks[h]
			try {
				hookFn(record)
			} catch (err: Exception) {
				try {
					sout("Logger hook failure: " + err)
				} catch (fallbackErr: Exception) {
					/* swallow secondary failure */
				}
			}
			h = h + 1
		}
	}

	intent _log(levelValue, message: string, extra: Optional[dict] = null, err: Optional[any] = null) {
		var normalizedLevel = LogLevel.normalize(levelValue)
		if (not LogLevel.is_enabled(normalizedLevel, this.level)) {
			return
		}

		var context = this._build_context(extra)
		var record = new LogRecord(normalizedLevel, message, this.name, context, err, this._callsite(), this.emitterModule)
		this._dispatch(record)
	}

	intent debug(message: string, extra: Optional[dict] = null) { this._log(LogLevel.DEBUG, message, extra, null); return null }
	intent info(message: string, extra: Optional[dict] = null) { this._log(LogLevel.INFO, message, extra, null); return null }
	intent warning(message: string, extra: Optional[dict] = null) { this._log(LogLevel.WARNING, message, extra, null); return null }
	intent warn(message: string, extra: Optional[dict] = null) { this._log(LogLevel.WARNING, message, extra, null); return null }
	intent error(message: string, extra: Optional[dict] = null, err: Optional[any] = null) { this._log(LogLevel.ERROR, message, extra, err); return null }
	intent critical(message: string, extra: Optional[dict] = null, err: Optional[any] = null) { this._log(LogLevel.CRITICAL, message, extra, err); return null }
	intent exception(err, message: Optional[string] = null, extra: Optional[dict] = null) {
		var msg = message == null ? "Unhandled exception" : message
		this._log(LogLevel.ERROR, msg, extra, err)
		return null
	}
}


var console = new Logger("core", LogLevel.DEBUG, null, {})
