from src.corplang.runtime.intelligence import (
    get_provider_registry,
    IntelligenceProvider,
    IntelligenceConfig,
    ExecutionResult,
    ExecutionAction,
)
from src.corplang.runtime import get_agent_manager


class TestProvider(IntelligenceProvider):
    def initialize(self, config: IntelligenceConfig) -> None:
        self.config = config

    def invoke(self, messages, context):
        # Return an ExecutionResult that runs simple python code
        code = 'print("hello-from-provider")'
        action = ExecutionAction(type="run_code", language="python", code=code)
        return ExecutionResult(status="ok", final=True, language="python", actions=[action])

    async def train(self, data, config):
        return True

    def embed(self, items):
        return [[0.0] * 8 for _ in items]

    def cleanup(self):
        pass


def test_agent_provider_flow(tmp_path):
    registry = get_provider_registry()
    registry.register("testprov", TestProvider)

    # Create a fake agent definition simple object
    class FakeInt:
        provider = "testprov"

    class FakeDef:
        name = "a1"
        intelligence = FakeInt()

    mgr = get_agent_manager()
    mgr.create_agent(FakeDef)

    result = mgr.predict_agent("a1", "run")

    # Ensure run metadata exists and stdout contains our print
    assert result.status == "ok"
    runs = result.metadata.get("runs", [])
    assert len(runs) == 1
    stdout = runs[0].get("stdout", "")
    assert "hello-from-provider" in stdout
