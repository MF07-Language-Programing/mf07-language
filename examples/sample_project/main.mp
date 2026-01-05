import examples.sample_project.lib.utils;

var total: float = 0.0;

async intent compute_async(x: int, y: int) : float {
    return sum(x, y);
}

intent g(): float {
    return 12.5
}

async intent run(){
    var a: int = 10;
    var b: int = 20;
    var task = compute_async(a, b);
    var result = await task;
    print("Async sum result:", result);

    var ds = dataset load users("users.csv");
    model create clf;
    model train clf (dataset="users");
    model predict clf;

    var obj = {"name": "Lucas", "active": true, "employees": 15};
    print("company name:", obj.name)
    print("company is active:", obj.active)
    print("Obj:", JSON.stringify(obj));
    print("")
}


await run();

total = await compute_async(5, 15);
total = total + 5.5
var type_value = type(total)
print("type: {type_value}")
print("value: {total}")
print("=============================")

var ab: float = g()
var type_value_a = type(ab)
print("VALUE: {a}")
print("TEST: {type_value_a}")
print("=============================")
