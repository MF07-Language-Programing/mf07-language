intent calculate_tax(amount) {
    return amount * 0.2;
}

agent ConsoleAssistant {
    intelligence { provider auto }
    context { allow intent calculate_tax }
    execution { interactive true }
}

agent Counch {
    intelligence { provider auto }
    context { deny intent calculate_tax }
    execution { interactive true }
}

# Start a stdin loop with two agents. Prefix with 'Counch:' to route to Counch, otherwise input goes to ConsoleAssistant.
loop stdin using ConsoleAssistant, Counch
