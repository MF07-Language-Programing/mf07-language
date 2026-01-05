
var logger = new Logger(LogLevel.DEBUG, "ExampleObject")

class ExampleObject {
    var name: string

    intent constructor(name: Optional[string] = "Dorival-Totoso") {
        this.name = name
    }

    intent greet() {
        logger.info("Hello from " + this.name)
    }

    intent getName(): string {
        return this.name
    }
}

async intent main() {
	var example_obj = new ExampleObject()
	print("ObjectType={type(example_obj)}")
	print("ObjectType_Base={type(ExampleObject)}")
	print("ObjectType={example_obj.name}")
}

await main()
