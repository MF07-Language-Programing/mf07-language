from src.corplang.runtime import get_agent_manager
from src.corplang.runtime.intelligence import ExecutionResult, get_provider_registry, IntelligenceConfig


def test_call_corp_function_using_context_env():
    mgr = get_agent_manager()

    def main(name=None):
        print(f"Hello from main, name={name}")
        return f"Response from main, name={name}" 

    class FakeInt:
        provider = "placeholder"

    class FakeDef:
        name = "TestAgent"
        intelligence = FakeInt()

    # Create agent without snapshot
    mgr.create_agent(FakeDef, env_snapshot={})

    # Ask agent to call function by name, passing context_env that contains the function
    res = mgr.predict_agent("TestAgent", "call main", context_env={"main": main})
    assert isinstance(res, ExecutionResult)
    assert res.status in ("awaiting_input", "ok", "error")

    # Provide params in value form
    res2 = mgr.predict_agent("TestAgent", "value:name=Joe", context_env={"main": main})
    assert getattr(res2, "status", None) == "ok"
    assert res2.final is True
    assert res2.metadata.get("call_result") or res2.metadata.get("runs")
    # Verify result present
    call_results = res2.metadata.get("call_result") or []
    if call_results:
        assert call_results[0]["fn"] == "main"
        assert "Response from main" in call_results[0]["result"]
    else:
        # alternatively check runs result if call used run
        runs = res2.metadata.get("runs") or []
        assert runs and runs[0]["status"] == "ok"
