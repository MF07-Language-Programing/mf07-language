"""Exemplo MF07: interface, classes, herança, interpolação, logger e tipagem."""

from examples.myproject.domain.greeter import GreetingProvider, GreeterFactory
from examples.myproject.services.audit_service import AuditService
from examples.myproject.utils.math_utils import accumulate, scale_first, describe_sign
from examples.myproject.utils.text_utils import format_message, build_provider_meta


intent main() {
	"""Fluxo principal de demonstração."""

	print(f"Starting MF07 AST demo: {StringHelpers.find('lucas', 's')}")

	var factory = new GreeterFactory()
	var greeter: GreetingProvider = factory.create(excited=true)
	var message: string = greeter.greet(name="MF07 developer")
	var formatted: string = format_message("Greeting", text=message, suffix="!!")

	print(f"Greeting built: {message}")
	print(message)
	print(formatted)

	var meta: string = build_provider_meta(provider=greeter)
	print("Meta describe:")
	print(meta)

	var numbers: List[int] = [1, 3, 5]
	var total: int = accumulate(numbers)
	var scaled_first: int = scale_first(numbers, factor=10)
	var summary: string = f"total={total} scaled_first={scaled_first}"
	print(summary)
	print(describe_sign(total))
	print(describe_sign(value=-5))

	print("Demo finished")
}

await main()
