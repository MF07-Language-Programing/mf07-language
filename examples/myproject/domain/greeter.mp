interface GreetingProvider {
    """Contrato: gera uma saudação textual."""
    intent greet(name: string): string
}

class BaseGreeter implements GreetingProvider {
    """Implementação simples que atende ao contrato da interface."""
    intent greet(name: string): string {
        return f"Hello {name}"
    }
}

class ExcitedGreeter extends BaseGreeter {
    """Override mantendo assinatura e tipo de retorno do pai."""
    intent greet(name: string): string {
        return f"Hello {name}!"
    }
}

class GreeterFactory {
    """Cria providers com base em flags simples."""
    intent create(excited: bool): GreetingProvider {
        if (excited) {
            return new ExcitedGreeter()
        }
        return new BaseGreeter()
    }
}
