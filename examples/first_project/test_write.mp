"""Test file write."""

async intent main() {
    var data = {
        "name": "Test",
        "value": 123
    }
    
    var json_str = JSON.stringify(data, indent=2)
    print("Writing JSON...")
    
    var filePath = Path.join(Path.cwd(), "tests", "test.json")
    var workdir = new Directory(Path.join(Path.cwd(), "tests"))
    if (not workdir.exists()) {
        workdir.ensure()
    }
    
    with open(filePath, "w") as f {
        print(f"File opened: {f}")
        var ok = await f.writeText(json_str, null)
        print(f"Write result: {ok}")
    }
    
    print("Done!")
}

await main()
