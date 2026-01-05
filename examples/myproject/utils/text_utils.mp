from examples.myproject.domain.greeter import GreetingProvider

intent format_message(prefix: string, text: string, suffix: string = "!"): string {
    return f"{prefix}: {text}{suffix}"
}

intent build_provider_meta(provider: GreetingProvider): string {
    var provider_type: string = type(provider)
    return f"provider={provider_type}"
}
