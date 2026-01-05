# Test module for import - tax_module.mp
# This file defines components that can be imported

intent calculate_tax(amount) {
    return amount * 0.2;
}

class TaxHelper {
    var default_rate = 0.15

    func calculate_with_rate(amount, rate) {
        return amount * rate;
    }

    func calculate_default(amount) {
        return self.calculate_with_rate(amount, self.default_rate);
    }
}

# Export some values
var TAX_RATE = 0.25
var MODULE_NAME = "tax_module"