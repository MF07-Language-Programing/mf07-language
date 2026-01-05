"""Test JSON formatting with indent parameter."""

intent test_json_formatting() {
    print("=== Test JSON Formatting ===")
    
    var data = {
        "name": "Lucas",
        "age": 25,
        "address": {
            "city": "São Paulo",
            "country": "Brazil"
        },
        "hobbies": ["coding", "music", "gaming"]
    }
    
    print("\n1. Compact JSON (no indent):")
    var compact = JSON.stringify(data)
    print(compact)
    
    print("\n2. Formatted JSON (indent=2):")
    var formatted = JSON.stringify(data, null, 2)
    print(formatted)
    
    print("\n3. Formatted JSON with named parameter (indent=4):")
    var formatted4 = JSON.stringify(data, indent=4)
    print(formatted4)
    
    print("\n4. Parse formatted JSON back:")
    var parsed = JSON.parse(formatted)
    print(f"Name: {parsed.name}, City: {parsed.address.city}")
    
    print("\n=== Test Complete ===")
}

test_json_formatting()
