"""Generic typed list collection using native generics."""

from core.lang.Iterable import Iterable
from core.lang.Iterator import Iterator
from core.lang.exceptions import GenericContractError

class ListIterator<T> implements Iterator<T> {
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

class List<T> implements Iterable<T> {
	private var data: array

	intent constructor(values = null) {
		this.data = []
		if (values != null) {
			if (type(values) == "list") {
				var i = 0
				while (i < len(values)) {
					this.data.append(values[i])
					i = i + 1
				}
			} else {
				var iter = values.__iter__()
				while (iter.hasNext()) {
					this.data.append(iter.next())
				}
			}
		}
	}

	intent iterator(): Iterator<T> {
		return new ListIterator(this.data)
	}

	intent __iter__(): Iterator<T> {
		return this.iterator()
	}

	intent size(): int {
		return len(this.data)
	}

	intent isEmpty(): bool {
		return len(this.data) == 0
	}

	intent clear() {
		this.data = []
	}

	intent append(item: T): bool {
		var generics = genericOf(this)
		if (len(generics) > 0 and "T" in generics) {
			var expected = generics["T"]
			var actual = typeOf(item)
			if (not actual.isAssignableTo(expected)) {
				var msg = "RuntimeTypeError:\n" +
					"Expected element of type " + expected.display_name + "\n" +
					"Got " + actual.display_name + "\n" +
					"While mutating List<" + expected.display_name + ">"
				throw new GenericContractError(msg)
			}
		}
		this.data.append(item)
		return true
	}

	intent get(index: int): T {
		var size = len(this.data)
		if (index >= 0 and index < size) {
			return this.data[index]
		}
		return null
	}

	intent length(): int {
		return len(this.data)
	}

	intent __raw__() {
		return this.data
	}

	intent toString(): string {
		var size = len(this.data)
		if (size == 0) {
			return "[]"
		}

		var result = "["
		var i = 0
		while (i < size) {
			if (i > 0) {
				result = result + ", "
			}
			var item = this.data[i]
			result = result + str(item)
			i = i + 1
		}
		result = result + "]"
		return result
	}
}
