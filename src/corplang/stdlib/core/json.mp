"""JSON module - Complete JSON parsing and serialization support."""

import core.io.fs

class JSON {
    """
    JSON parsing and serialization utilities.
    Provides methods for converting between JSON strings and objects.
    """
    
    # Parse JSON string to object
    intent parse(text: string) {
        """
        Parse a JSON string into an object.
        
        Args:
            text: JSON string to parse
            
        Returns:
            Parsed object (dict, list, string, number, bool, or null)
            
        Example:
            var obj = JSON.parse('{"name": "John", "age": 30}')
            print(obj.name)  # John
        """
        try {
            return mf.json.parse(text)
        } catch (e: Exception) {
            throw new RuntimeException(f"Failed to parse JSON: {e}")
        }
    }
    
    # Stringify object to JSON string
    intent stringify(value, replacer, indent: int) {
        """
        Convert an object to JSON string.
        
        Args:
            value: Object to convert to JSON
            replacer: (Optional) Function or array to transform values (not yet implemented)
            indent: (Optional) Number of spaces for indentation (default: 0 = compact)
            
        Returns:
            JSON string representation
            
        Example:
            var json = JSON.stringify({"name": "John", "age": 30}, null, 2)
            # Returns formatted JSON with 2-space indentation
            
            # Using named parameter:
            var json = JSON.stringify(obj, indent=2)
        """
        try {
            # Pass indent directly to mf.json.stringify for proper formatting
            if (indent != null and indent > 0) {
                return mf.json.stringify(value, indent)
            }
            
            return mf.json.stringify(value)
        } catch (e: Exception) {
            throw new RuntimeException(f"Failed to stringify JSON: {e}")
        }
    }
    
    # Pretty print JSON with indentation (deprecated, use stringify with indent)
    intent _prettyPrint(jsonStr: string, indent: int): string {
        """Internal: Format JSON string with indentation."""
        try {
            var obj = mf.json.parse(jsonStr)
            return mf.json.stringify(obj, indent)
        } catch (e: Exception) {
            return jsonStr
        }
    }
    
    # Load JSON from file
    async intent loadFile(filePath: string) {
        """
        Load and parse JSON from a file.
        
        Args:
            filePath: Path to JSON file
            
        Returns:
            Parsed JSON object
            
        Example:
            var data = await JSON.loadFile("config.json")
            print(data.version)
        """
        try {
            var file = new File(filePath)
            var content = await file.readText("")
            return JSON.parse(content)
        } catch (e: Exception) {
            throw new RuntimeException(f"Failed to load JSON from {filePath}: {e}")
        }
    }
    
    # Save object as JSON to file
    async intent saveFile(filePath: string, value, indent: int) {
        """
        Save object as JSON to a file.
        
        Args:
            filePath: Path to save JSON file
            value: Object to save as JSON
            indent: (Optional) Number of spaces for indentation
            
        Returns:
            true if successful, false otherwise
            
        Example:
            var data = {"name": "John", "age": 30}
            var ok = await JSON.saveFile("data.json", data, 2)
            # Or with named parameter:
            var ok = await JSON.saveFile("data.json", data, indent=2)
        """
        try {
            var jsonStr = JSON.stringify(value, null, indent)
            var file = new File(filePath)
            return await file.writeText(jsonStr, null)
        } catch (e: Exception) {
            throw new RuntimeException(f"Failed to save JSON to {filePath}: {e}")
        }
    }
    
    # Check if string is valid JSON
    intent isValid(text: string): bool {
        """
        Check if a string is valid JSON.
        
        Args:
            text: String to validate
            
        Returns:
            true if valid JSON, false otherwise
            
        Example:
            if (JSON.isValid('{"name": "John"}')) {
                print("Valid JSON")
            }
        """
        try {
            JSON.parse(text)
            return true
        } catch (e: Exception) {
            return false
        }
    }
    
    # Deep clone an object via JSON serialization
    intent clone(value) {
        """
        Create a deep clone of an object using JSON serialization.
        Note: This only works for JSON-serializable objects.
        
        Args:
            value: Object to clone
            
        Returns:
            Deep cloned copy
            
        Example:
            var original = {"name": "John", "nested": {"value": 42}}
            var copy = JSON.clone(original)
            copy.nested.value = 100
            print(original.nested.value)  # Still 42
        """
        try {
            var jsonStr = JSON.stringify(value, null, 0)
            return JSON.parse(jsonStr)
        } catch (e: Exception) {
            throw new RuntimeException(f"Failed to clone object: {e}")
        }
    }
    
    # Merge two JSON objects
    intent merge(target, source) {
        """
        Merge source object into target object (shallow merge).
        
        Args:
            target: Target object to merge into
            source: Source object to merge from
            
        Returns:
            Merged object
            
        Example:
            var a = {"x": 1, "y": 2}
            var b = {"y": 3, "z": 4}
            var merged = JSON.merge(a, b)
            # Result: {"x": 1, "y": 3, "z": 4}
        """
        if (target == null) { target = {} }
        if (source == null) { return target }
        
        try {
            var keys = Object.keys(source)
            for (var key in keys) {
                target[key] = source[key]
            }
            return target
        } catch (e: Exception) {
            throw new RuntimeException(f"Failed to merge objects: {e}")
        }
    }
    
    # Get value at JSON path
    intent get(obj, path: string, defaultValue) {
        """
        Get value from object using dot-notation path.
        
        Args:
            obj: Object to query
            path: Dot-notation path (e.g., "user.address.city")
            defaultValue: (Optional) Value to return if path not found
            
        Returns:
            Value at path or defaultValue
            
        Example:
            var data = {"user": {"name": "John", "address": {"city": "NYC"}}}
            var city = JSON.get(data, "user.address.city", "Unknown")
            # Returns: "NYC"
        """
        if (obj == null) { return defaultValue }
        
        try {
            var parts = path.split(".")
            var current = obj
            
            for (var part in parts) {
                if (current == null) { return defaultValue }
                current = current[part]
            }
            
            if (current != null) {
                return current
            } else {
                return defaultValue
            }
        } catch (e: Exception) {
            return defaultValue
        }
    }
}

# Export convenience functions at module level for easier access
intent parse(text: string) {
    return JSON.parse(text)
}

intent stringify(value, replacer, indent: int) {
    return JSON.stringify(value, replacer, indent)
}

async intent loadFile(filePath: string) {
    return await JSON.loadFile(filePath)
}

async intent saveFile(filePath: string, value, indent: int) {
    return await JSON.saveFile(filePath, value, indent)
}

intent isValid(text: string): bool {
    return JSON.isValid(text)
}

intent clone(value) {
    return JSON.clone(value)
}

intent merge(target, source) {
    return JSON.merge(target, source)
}

intent get(obj, path: string, defaultValue) {
    return JSON.get(obj, path, defaultValue)
}
