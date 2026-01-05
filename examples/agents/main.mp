# Test file for import system - main.mp
# This file demonstrates importing tax_module.mp and using its components

# Import the tax_module
from tax_module import TaxCalculator, MessageSender, calculate_tax, TaxHelper

# Define some test classes and functions
class TaxCalculator {
    var rate = 0.2

    func calculate(amount) {
        return amount * self.rate
    }
}

class MessageSender {
    func send_message(msg) {
        print("Sending message: " + msg)
        return true
    }
}

# Instantiate classes
var calculator = TaxCalculator()
var sender = MessageSender()

# Send some test messages
sender.send_message("Testing import system")
sender.send_message("Calculator rate: " + str(calculator.rate))

# Calculate tax using local class
var tax = calculator.calculate(100)
print("Local tax calculation: $" + str(tax))

# Now use the imported components from tax_module
print("Imported module name: " + tax_module.MODULE_NAME)
print("Imported tax rate: " + str(tax_module.TAX_RATE))

# Call the imported intent
var imported_tax = calculate_tax(200)
print("Imported tax calculation (intent): $" + str(imported_tax))

# Instantiate imported class
var helper = TaxHelper()
var helper_tax = helper.calculate_default(300)
print("Imported class calculation: $" + str(helper_tax))

var custom_tax = helper.calculate_with_rate(300, 0.3)
print("Imported class custom rate: $" + str(custom_tax))

print("Import system test completed successfully!")