class Test {
    private var data = "test"
    
    intent privateMethod() {
        return this.data
    }
    
    intent publicMethod() {
        return this.privateMethod()
    }
}

var t = new Test()
print(t.publicMethod())
