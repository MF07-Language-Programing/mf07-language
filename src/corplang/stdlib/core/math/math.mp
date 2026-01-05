class Math {
    # Constants
    static var PI: float = 3.141592653589793
    static var E: float = 2.718281828459045
    static var TAU: float = 6.283185307179586
    static var INF: float = __native__("float", "inf")
    static var NAN: float = __native__("float", "nan")

    # Basic operations
    static intent abs(x: float): float {
        """Return absolute value of x"""
        return __native__("abs", x)
    }

    static intent ceil(x: float): int {
        """Return ceiling of x (smallest integer >= x)"""
        return __native__("math.ceil", x)
    }

    static intent floor(x: float): int {
        """Return floor of x (largest integer <= x)"""
        return __native__("math.floor", x)
    }

    static intent round(x: float, digits: int = 0): float {
        """Round x to given number of decimal digits"""
        return __native__("round", x, digits)
    }

    static intent sqrt(x: float): float {
        """Return square root of x"""
        return __native__("math.sqrt", x)
    }

    static intent pow(x: float, y: float): float {
        """Return x raised to power y"""
        return __native__("pow", x, y)
    }

    # Trigonometric
    static intent sin(x: float): float {
        """Return sine of x (x in radians)"""
        return __native__("math.sin", x)
    }

    static intent cos(x: float): float {
        """Return cosine of x (x in radians)"""
        return __native__("math.cos", x)
    }

    # Comparison
    static intent min(a: float, b: float): float {
        """Return minimum of a and b"""
        return __native__("min", a, b)
    }

    static intent max(a: float, b: float): float {
        """Return maximum of a and b"""
        return __native__("max", a, b)
    }
}
