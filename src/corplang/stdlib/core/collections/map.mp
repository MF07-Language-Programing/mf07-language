"""Generic key-value map using native generics."""

from core.lang.Iterable import Iterable
from core.lang.Iterator import Iterator
from core.lang.exceptions import GenericContractError

class MapIterator<K, V> implements Iterator<array> {
	private var keys: array
	private var data: dict
	private var index: int

	intent constructor(data: dict) {
		this.data = data
		this.keys = []
		for (var k in data) {
			this.keys.append(k)
		}
		this.index = 0
	}

	intent hasNext(): bool {
		return this.index < len(this.keys)
	}

	intent next(): array {
		if (not this.hasNext()) {
			return null
		}
		var key = this.keys[this.index]
		var value = this.data[key]
		this.index = this.index + 1
		return [key, value]
	}
}

class Map<K, V> implements Iterable<array> {
	private var data: dict

	intent constructor(initial: dict = null) {
		if (initial == null) {
			this.data = {}
		} else {
			this.data = initial
		}
	}

	intent iterator(): Iterator<array> {
		return new MapIterator(this.data)
	}

	intent __iter__(): Iterator<array> {
		return this.iterator()
	}

	intent put(key: K, value: V) {
		var generics = genericOf(this)
		if (len(generics) > 0) {
			if ("K" in generics) {
				var expectedK = generics["K"]
				var actualK = typeOf(key)
				if (not actualK.isAssignableTo(expectedK)) {
					var msg = "RuntimeTypeError:\n" +
						"Expected key of type " + expectedK.display_name + "\n" +
						"Got " + actualK.display_name + "\n" +
						"While mutating Map<" + expectedK.display_name + ", ...>"
					throw new GenericContractError(msg)
				}
			}
			if ("V" in generics) {
				var expectedV = generics["V"]
				var actualV = typeOf(value)
				if (not actualV.isAssignableTo(expectedV)) {
					var msg = "RuntimeTypeError:\n" +
						"Expected value of type " + expectedV.display_name + "\n" +
						"Got " + actualV.display_name + "\n" +
						"While mutating Map<..., " + expectedV.display_name + ">"
					throw new GenericContractError(msg)
				}
			}
		}
		this.data[key] = value
	}
    
	intent get(key: K): V {
		if (key in this.data) {
			return this.data[key]
		}
		return null
	}

	intent has(key: K): bool {
		return key in this.data
	}

	intent remove(key: K): bool {
		if (key in this.data) {
			del this.data[key]
			return true
		}
		return false
	}

	intent clear() {
		this.data = {}
	}

	intent size(): int {
		return len(this.data)
	}

	intent keys(): array {
		var result = []
		for (var k in this.data) {
			result.append(k)
		}
		return result
	}

	intent values(): array {
		var result = []
		for (var k in this.data) {
			result.append(this.data[k])
		}
		return result
	}

	intent entries(): array {
		var result = []
		for (var k in this.data) {
			result.append([k, this.data[k]])
		}
		return result
	}

	intent __raw__() {
		return this.data
	}

	intent toString(): string {
		var s = "{"
		var keyArray = []
		for (var k in this.data) {
			keyArray.append(k)
		}
		var i = 0
		while (i < len(keyArray)) {
			var key = keyArray[i]
			var value = this.data[key]
			var keyStr = str(key)
			if (type(key) == "str") {
				keyStr = "\"" + key + "\""
			}
			var valueStr = str(value)
			if (type(value) == "str") {
				valueStr = "\"" + value + "\""
			}
			s = s + keyStr + ": " + valueStr
			if (i < len(keyArray) - 1) {
				s = s + ", "
			}
			i = i + 1
		}
		s = s + "}"
		return s
	}
}
