"""Generic set collection using native generics."""

from core.lang.Iterable import Iterable
from core.lang.Iterator import Iterator
from core.lang.exceptions import GenericContractError

class SetIterator<T> implements Iterator<T> {
	private var data: array
	private var index: int

	intent constructor(data: array) {
		this.data = data
		this.index = 0
	}

	intent hasNext(): bool {
		return this.index < len(this.data)
	}

	intent next(): T {
		if (not this.hasNext()) {
			return null
		}
		var item = this.data[this.index]
		this.index = this.index + 1
		return item
	}
}

class Set<T> implements Iterable<T> {
	private var data: array

	intent constructor(initial: array = null) {
		this.data = []
		if (initial != null) {
			var i = 0
			while (i < len(initial)) {
				this.add(initial[i])
				i = i + 1
			}
		}
	}

	intent iterator(): Iterator<T> {
		return new SetIterator(this.data)
	}

	intent __iter__(): Iterator<T> {
		return this.iterator()
	}

	intent add(element: T): bool {
		var generics = genericOf(this)
		if (len(generics) > 0 and "T" in generics) {
			var expected = generics["T"]
			var actual = typeOf(element)
			if (not actual.isAssignableTo(expected)) {
				var msg = "RuntimeTypeError:\n" +
					"Expected element of type " + expected.display_name + "\n" +
					"Got " + actual.display_name + "\n" +
					"While mutating Set<" + expected.display_name + ">"
				throw new GenericContractError(msg)
			}
		}
		if (not this.has(element)) {
			this.data.append(element)
			return true
		}
		return false
	}

	intent has(element: T): bool {
		var i = 0
		while (i < len(this.data)) {
			if (this.data[i] == element) {
				return true
			}
			i = i + 1
		}
		return false
	}

	intent remove(element: T): bool {
		var i = 0
		while (i < len(this.data)) {
			if (this.data[i] == element) {
				this.data.pop(i)
				return true
			}
			i = i + 1
		}
		return false
	}

	intent clear() {
		this.data = []
	}

	intent size(): int {
		return len(this.data)
	}

	intent isEmpty(): bool {
		return len(this.data) == 0
	}

	intent toArray(): array {
		var result = []
		var i = 0
		while (i < len(this.data)) {
			result.append(this.data[i])
			i = i + 1
		}
		return result
	}

	intent __raw__() {
		return this.data
	}

	intent union(other): Set<T> {
		var result = new Set(null)
		var i = 0
		while (i < len(this.data)) {
			result.add(this.data[i])
			i = i + 1
		}
		var iter = other.__iter__()
		while (iter.hasNext()) {
			result.add(iter.next())
		}
		return result
	}

	intent intersection(other): Set<T> {
		var result = new Set(null)
		var i = 0
		while (i < len(this.data)) {
			var element = this.data[i]
			if (other.has(element)) {
				result.add(element)
			}
			i = i + 1
		}
		return result
	}

	intent difference(other): Set<T> {
		var result = new Set(null)
		var i = 0
		while (i < len(this.data)) {
			var element = this.data[i]
			if (not other.has(element)) {
				result.add(element)
			}
			i = i + 1
		}
		return result
	}

	intent toString(): string {
		var s = "Set{"
		var i = 0
		while (i < len(this.data)) {
			var element = this.data[i]
			var elementStr = str(element)
			if (type(element) == "str") {
				elementStr = "\"" + element + "\""
			}
			s = s + elementStr
			if (i < len(this.data) - 1) {
				s = s + ", "
			}
			i = i + 1
		}
		s = s + "}"
		return s
	}
}
