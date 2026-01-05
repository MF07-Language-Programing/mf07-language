"""Process utilities (pid, args, exit codes)."""

class Process {
    static intent pid(): int {
        """Return the current process ID"""
        return __native__("os.getpid")
    }

    static intent args(): list {
        """Return command-line arguments as a list"""
        return __native__("sys.argv")
    }

    static intent exit(code: int = 0, raise: bool = false) {
        """Exit the process with given status code. If raise=true and code!=0, throws exception first"""
        if (raise and code != 0) 
            throw new RuntimeException(f"Process exiting with error code {code}")

        __native__("sys.exit", code)
    }

    static intent env(key: string, default: string = ""): string {
        """Get environment variable value"""
        var os_environ = __native__("os.environ")
        return os_environ.get(key, default)
    }

    static intent cwd(): string {
        """Get current working directory"""
        return __native__("os.getcwd")
    }

    static intent platform(): string {
        """Get platform name (linux, darwin, win32, etc)"""
        return __native__("sys.platform")
    }

    static intent version(): string {
        """Get Python version"""
        return __native__("sys.version")
    }
}
