"""Intelligence provider contracts for AI integration (placeholder)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass


@dataclass
class IntelligenceConfig:
    """Configuration extracted from AgentIntelligenceBlock."""
    
    provider: str = "auto"
    capability: Optional[str] = None
    training: Optional[str] = None
    model: Optional[str] = None
    extra: Dict[str, Any] = None
    
    @classmethod
    def from_ast(cls, intelligence_block: Any) -> "IntelligenceConfig":
        """Extract config from AgentIntelligenceBlock AST node."""
        if not intelligence_block:
            return cls()
        
        return cls(
            provider=getattr(intelligence_block, "provider", "auto") or "auto",
            capability=getattr(intelligence_block, "capability", None),
            training=getattr(intelligence_block, "training", None),
            extra=getattr(intelligence_block, "entries", {})
        )


from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ExecutionAction:
    """Action requested by a provider; executed by the runtime."""
    type: str  # e.g., run_code, write_file, read_file, call_fn, log, finalize
    language: Optional[str] = None
    code: Optional[Union[str, Dict[str, str]]] = None
    args: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Structured, executable response from an intelligence provider."""
    status: str = "ok"  # ok | error | pending
    final: bool = True
    language: Optional[str] = None
    code: Optional[Union[str, Dict[str, str]]] = None
    actions: List[ExecutionAction] = field(default_factory=list)
    output: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntelligenceProvider(ABC):
    """Abstract AI provider returning ExecutionResult."""

    @abstractmethod
    def initialize(self, config: IntelligenceConfig) -> None:
        """Initialize provider with config."""
        pass

    @abstractmethod
    def invoke(
        self,
        messages: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """Run inference and return an ExecutionResult."""
        pass

    @abstractmethod
    async def train(self, data: Any, config: IntelligenceConfig) -> bool:
        """Train or fine-tune provider."""
        pass

    @abstractmethod
    def embed(self, items: List[str]) -> List[List[float]]:
        """Create embeddings for items."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup provider resources."""
        pass


class ProviderRegistry:
    """
    Registry for intelligence provider implementations.

    PLACEHOLDER: Register concrete providers here.
    """

    def __init__(self):
        self._providers: Dict[str, type] = {}

    def register(self, name: str, provider_class: type) -> None:
        """Register a provider implementation."""
        if not issubclass(provider_class, IntelligenceProvider):
            raise TypeError(f"{provider_class} must inherit IntelligenceProvider")

        self._providers[name] = provider_class

    def get(self, name: str) -> Optional[type]:
        """Get registered provider class by name."""
        return self._providers.get(name)

    def create(self, name: str, config: IntelligenceConfig) -> Optional[IntelligenceProvider]:
        """Instantiate and initialize a provider."""
        provider_class = self.get(name)
        if not provider_class:
            return None

        instance = provider_class()
        instance.initialize(config)
        return instance

    def list_providers(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())


# Global singleton
_provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry."""
    return _provider_registry


# EXTENSION POINT: Example placeholder provider
class PlaceholderProvider(IntelligenceProvider):
    """Stub provider for testing without AI backend."""

    def initialize(self, config: IntelligenceConfig) -> None:
        self.config = config

    def invoke(self, messages: List[Dict[str, str]], context: Dict[str, Any]) -> ExecutionResult:
        """Simple interactive provider: detect function intent and request missing args."""
        last = messages[-1]["content"] if messages else ""
        txt = last.strip() if isinstance(last, str) else ""

        functions = (context or {}).get("functions") or []
        # Natural language attempt: find a function mention
        target_fn = None
        for f in functions:
            name = f.get("name", "")
            if name and name.lower() in txt.lower():
                target_fn = f
                break

        # If explicit 'call fn' used
        if txt.lower().startswith("call ") and not target_fn:
            import re
            m = re.match(r"call\s+([a-zA-Z_][\w]*)", txt, re.IGNORECASE)
            if m:
                fn = m.group(1)
                for f in functions:
                    if f.get("name") == fn:
                        target_fn = f
                        break

        if target_fn:
            # Check for inline params like 'call fn with (a=1,b=2)' or value:...
            import re
            m = re.search(r"with\s*\((.*?)\)", txt, re.IGNORECASE)
            params = {}
            if m:
                raw = m.group(1)
                for part in raw.split(","):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        k = k.strip()
                        v = v.strip()
                        if v.isdigit():
                            v = int(v)
                        params[k] = v
            if params:
                return ExecutionResult(status="ok", final=True, actions=[ExecutionAction(type="call_fn", args={"fn": target_fn.get("name"), "params": params})])

            # No params: request input with structured prompt listing parameters
            params_req = [p["name"] for p in (target_fn.get("params") or [])]
            prompt = f"Please provide parameters for {target_fn.get('name')}: {', '.join(params_req)} using 'value:key=val,..'"
            return ExecutionResult(status="ok", final=False, actions=[ExecutionAction(type="request_input", args={"prompt": prompt, "fn": target_fn.get("name"), "params": params_req})])

        # If user provided direct 'value:' response, treat as generic input
        if txt.lower().startswith("value:"):
            return ExecutionResult(status="ok", final=True, language="python", actions=[ExecutionAction(type="run_code", language="python", code=f'print("placeholder executed with value: {txt.split(":",1)[1].strip()}")')])

        # Else: try simple code execution or instruct the user
        return ExecutionResult(status="ok", final=False, actions=[ExecutionAction(type="request_input", args={"prompt": "I can run functions you have; tell me which function to call and with what args."})])

    async def train(self, data: Any, config: IntelligenceConfig) -> bool:
        return True

    def embed(self, items: List[str]) -> List[List[float]]:
        return [[0.0] * 128 for _ in items]

    def cleanup(self) -> None:
        pass


# Register placeholder by default
_provider_registry.register("placeholder", PlaceholderProvider)


# Try to auto-import wrappers (so they can self-register providers when present)
try:
    import importlib

    importlib.import_module("src.corplang.runtime.wrappers.ollama")
except Exception:
    # Do not fail import if optional wrappers or their deps are missing.
    pass