from core.utils.logger import console

class Test {
    intent show() {
        console.debug("Test message")
    }
}

var t = new Test()
t.show()
