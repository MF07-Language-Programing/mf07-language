from core.utils.logger import console

class Test {
    intent showConsole() {
        console.debug("Test from method")
    }
}

var t = new Test()
t.showConsole()
