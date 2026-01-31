from src.corplang.runtime.intelligence import get_provider_registry, IntelligenceConfig, ExecutionResult


def test_ollama_provider_registered_and_handles_missing_client():
    prov_cls = get_provider_registry().get("ollama")
    assert prov_cls is not None

    cfg = IntelligenceConfig(provider="ollama")
    prov = prov_cls()
    prov.initialize(cfg)

    # Calling invoke without ollama client installed should return an ExecutionResult
    res = prov.invoke([{"role": "user", "content": "print('hi')"}], {})
    assert isinstance(res, ExecutionResult)
    assert res.status in ("ok", "error")
    if res.status == "error":
        assert "ollama" in str(res.output).lower() or "not installed" in res.metadata.get("error", "").lower()
