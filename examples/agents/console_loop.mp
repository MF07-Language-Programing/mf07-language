intent calculate_tax(amount) {
    return amount * 0.2;
}

agent ConsoleAssistant {
    intelligence {
        provider auto
        mode conversational
    }

    context {
        allow intent calculate_tax
        deny filesystem
    }

    execution {
        interactive true
    }
}

# Start a stdin loop using ConsoleAssistant. Type 'describe' or 'call calculate_tax' or 'exit'.
loop stdin using ConsoleAssistant