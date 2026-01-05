from core.utils.logger import console

print("console:", console)
print("console type:", type(console))

class Test {
    intent show() {
        print("Inside method, console:", console)
    }
}

var t = new Test()
t.show()
