"""FIFO queue using native generics."""

from core.lang.Iterable import Iterable
from core.lang.Iterator import Iterator
from core.lang.exceptions import GenericContractError

class QueueIterator<T> implements Iterator<T> {
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

class Queue<T> implements Iterable<T> {
	private var data: array

	intent constructor(initial: array = null) {
		if (initial == null) {
			this.data = []
		} else {
			this.data = initial
		}
	}

	intent iterator(): Iterator<T> {
		return new QueueIterator(this.data)
	}

	intent __iter__(): Iterator<T> {
		return this.iterator()
	}

	intent enqueue(item: T) {
		var generics = genericOf(this)
		if (len(generics) > 0 and "T" in generics) {
			var expected = generics["T"]
			var actual = typeOf(item)
			if (not actual.isAssignableTo(expected)) {
				var msg = "RuntimeTypeError:\n" +
					"Expected element of type " + expected.display_name + "\n" +
					"Got " + actual.display_name + "\n" +
					"While mutating Queue<" + expected.display_name + ">"
				throw new GenericContractError(msg)
			}
		}
		this.data.append(item)
	}

	intent dequeue(): T {
		if (len(this.data) == 0) {
			return null
		}
		var item = this.data[0]
		this.data.pop(0)
		return item
	}

	intent peek(): T {
		if (len(this.data) == 0) {
			return null
		}
		return this.data[0]
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
