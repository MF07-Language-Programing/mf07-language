"""LIFO stack using native generics."""

from core.lang.Iterable import Iterable
from core.lang.Iterator import Iterator
from core.lang.exceptions import GenericContractError

class StackIterator<T> implements Iterator<T> {
	private var data: array
	private var index: int

	intent constructor(data: array) {
		this.data = data
		this.index = len(data) - 1
	}

	intent hasNext(): bool {
		return this.index >= 0
	}

	intent next(): T {
		if (not this.hasNext()) {
			return null
		}
		var item = this.data[this.index]
		this.index = this.index - 1
		return item
	}
}

class Stack<T> implements Iterable<T> {
	private var data: array

	intent constructor(initial: array = null) {
		if (initial == null) {
			this.data = []
		} else {
			this.data = initial
		}
	}

	intent iterator(): Iterator<T> {
		return new StackIterator(this.data)
	}

	intent __iter__(): Iterator<T> {
		return this.iterator()
	}

	intent push(item: T) {
		var generics = genericOf(this)
		if (len(generics) > 0 and "T" in generics) {
			var expected = generics["T"]
			var actual = typeOf(item)
			if (not actual.isAssignableTo(expected)) {
				var msg = "RuntimeTypeError:\n" +
					"Expected element of type " + expected.display_name + "\n" +
					"Got " + actual.display_name + "\n" +
					"While mutating Stack<" + expected.display_name + ">"
				throw new GenericContractError(msg)
			}
		}
		this.data.append(item)
	}

	intent pop(): T {
		if (len(this.data) == 0) {
			return null
		}
		var item = this.data[len(this.data) - 1]
		this.data.pop()
		return item
	}

	intent peek(): T {
		if (len(this.data) == 0) {
			return null
		}
		return this.data[len(this.data) - 1]
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

	intent __raw__() {
		return this.data
	}
}
