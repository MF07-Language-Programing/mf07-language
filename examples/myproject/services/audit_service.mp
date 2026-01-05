from examples.myproject.domain.greeter import GreetingProvider

class AuditService {
    private var logger: Logger

    intent constructor(logger: Logger) {
        this.logger = logger
    }

    intent audit_greeting(provider: GreetingProvider, name: string): string {
        var stamp = DateTime.now()
        var message: string = provider.greet(name)
        var formatted: string = f"[{stamp.format('%Y-%m-%d %H:%M:%S')}] provider={type(provider)} name={name} message={message}"
        this.logger.info(formatted)
        return formatted
    }

    intent summarize_lengths(messages: List[string]): int {
        var total: int = 0
        for (var msg in messages) {
            total = total + len(msg)
        }
        return total
    }
}
