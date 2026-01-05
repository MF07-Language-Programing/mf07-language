intent calculate_tax(amount) {
    return amount * 0.2;
}

agent HttpAssistant {
    intelligence {
        provider auto
    }

    context {
        allow intent calculate_tax
    }

    execution {
        interactive true
    }
}
