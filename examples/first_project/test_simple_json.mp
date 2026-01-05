"""Test simple JSON write."""

async intent main() {
    var data = {
        "name": "Test",
        "value": 123
    }
    
    var json_str = JSON.stringify(data, indent=2)
    print("JSON String:")
    print(json_str)
    print(f"\nType: {type(json_str)}")
}

await main()
