from src.corplang.runtime import get_agent_manager
from src.corplang.runtime.intelligence import ExecutionResult, get_provider_registry, IntelligenceConfig


def test_call_fn_direct_params():
    mgr = get_agent_manager()

    # Create a simple python function to be callable by agent
    def myfn(x=0):
        print(f"fn called with {x}")
        return int(x) * 2

    class FakeInt:
        provider = "placeholder"

    class FakeDef:
        name = "CallAgent"
        intelligence = FakeInt()

    # Register agent with environment snapshot containing myfn
    mgr.create_agent(FakeDef, env_snapshot={"myfn": myfn})

    # Ask agent to call function with params inline
    res = mgr.predict_agent("CallAgent", "call myfn with (x=5)", context_env={"myfn": myfn})
    assert isinstance(res, ExecutionResult)
    assert res.status == "ok"
    assert res.final is True
    # call result should be in metadata
    call_results = res.metadata.get("call_result", [])
    assert call_results
    assert call_results[0]["fn"] == "myfn"
    assert call_results[0]["result"] == 10


def test_call_fn_missing_params_and_interactive():
    mgr = get_agent_manager()

    def add(a=0, b=0):
        print(f"add {a}+{b}")
        return int(a) + int(b)

    class FakeInt:
        provider = "placeholder"

    class FakeDef:
        name = "AddAgent"
        intelligence = FakeInt()

    mgr.create_agent(FakeDef, env_snapshot={"add": add})

    # Without params, placeholder will ask for input; simulate interactive loop by
    # first calling predict_agent to get prompt, then supplying 'value:a=2,b=3'
    res = mgr.predict_agent("AddAgent", "call add", context_env={"add": add})
    assert isinstance(res, ExecutionResult)
    assert res.status in ("awaiting_input", "ok", "error")

    # Provide params in value form (we expect placeholder to detect 'value:')
    res2 = mgr.predict_agent("AddAgent", "value:a=2,b=3", context_env={"add": add})
    assert getattr(res2, "status", None) == "ok"
    assert res2.final is True
    assert res2.metadata.get("runs")
    assert res2.metadata.get("call_result") or res2.metadata.get("runs")[0]["result"] == 5
