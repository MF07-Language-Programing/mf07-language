class Random {
    static intent random(): float {
        """Return random float in range [0.0, 1.0)"""
        return __native__("random.random")
    }

    static intent rand(min: float = 0.0, max: float = 1.0): float {
        """Return random float in range [min, max]"""
        if (min == 0.0 and max == 1.0) {
            return __native__("random.random")
        }
        return __native__("random.uniform", min, max)
    }

    static intent randint(min: int = 0, max: int = 100): int {
        """Return random integer in range [min, max] inclusive"""
        return __native__("random.randint", min, max)
    }

    static intent choice(items: list): any {
        """Return random element from list"""
        return __native__("random.choice", items)
    }

    static intent string(length: int = 10): str {
        """Generate random alphanumeric string of given length"""
        var chars: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        var result: str = ""
        var i: int = 0
        while (i < length) {
            var idx: int = Random.randint(0, 61)
            result = result + chars[idx]
            i = i + 1
        }
        return result
    }
}
