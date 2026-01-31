import json
import re
from typing import Dict, Union
from pydantic import BaseModel, Field
try:
    from ollama import chat  # optional dependency
except Exception:
    chat = None

from ..intelligence import IntelligenceProvider


class CodeResponse(BaseModel):
    question: str
    code: Union[str, Dict[str, str]] = Field(
        ..., description="Código único ou múltiplos arquivos"
    )
    explanation: str
    language: str
    confidence: float = 0.95


class CopilotClient:
    """Copilot agent client from ollama."""
    _LANG_MAP: Dict[str, tuple] = {
        "python": ("python", "def", "class", "import"),
        "javascript": ("javascript", "js", "function", "async", "const", "let"),
        "bash": ("bash", "shell", "linux", "terminal", "sh"),
        "sql": ("sql", "select", "insert", "database", "tabela"),
        "html": ("html", "<", "css", "web"),
    }

    def __init__(self, model: str = "qwen2.5-coder:3b"):
        self.model = model

    def ask(self, question: str) -> CodeResponse:
        """Generete ask question."""
        lang = self._detect_language(question)
        prompt = self._build_prompt(question, lang)
        raw = self._call_model(prompt)
        return CodeResponse.model_validate(self._extract_json(raw))

    def _detect_language(self, question: str) -> str:
        q = question.lower()
        for lang, keywords in self._LANG_MAP.items():
            if any(k in q for k in keywords):
                return lang
        return "python"

    def _build_prompt(self, question: str, lang: str) -> str:
        """Building prompt."""
        return f"""
            CRIE UMA FUNÇÃO para: "{question}"
            
            RETORNE APENAS JSON VÁLIDO:
            
            {{
              "question": "{question}",
              "code": "CÓDIGO COMPLETO",
              "explanation": "explicação clara em português",
              "language": "{lang}",
              "confidence": 0.95
            }}
            
            NUNCA explique fora do JSON.
            NUNCA use outra linguagem além de {lang}.
            SE NECESSÁRIO, RETORNE MÚLTIPLOS ARQUIVOS NO CAMPO "code" COMO UM OBJETO JSON.
        """.strip()

    def _call_model(self, prompt: str) -> str:
        """Call the model backend."""
        if chat is None:
            raise RuntimeError("ollama client not installed")
        response = chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0},
        )
        return response["message"]["content"]

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Extract and normalize JSON-like LLM output."""
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("JSON não encontrado na resposta do modelo")

        raw = match.group()

        raw = raw.replace("\r", "")
        raw = raw.replace("\t", "    ")

        def _triple_quote_replacer(match: re.Match) -> str:
            content = match.group(1)
            escaped = (
                content
                .replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
            )
            return f"\"{escaped}\""

        raw = re.sub(
            r'"""\s*([\s\S]*?)\s*"""',
            _triple_quote_replacer,
            raw
        )

        raw = re.sub(r"`{1,3}", "", raw)

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print("\n--- JSON NORMALIZADO ---\n", raw)
            raise ValueError(f"JSON inválido após normalização: {e}") from e

    def ask_execution(self, question: str):
        """Return an ExecutionResult constructed from model JSON response."""
        from ..intelligence import ExecutionResult, ExecutionAction

        prompt = self._build_prompt(question, self._detect_language(question))
        # if the client lib is not installed, fail fast with clear message
        if chat is None:
            return ExecutionResult(status="error", final=True, output="ollama: client not installed", metadata={"error": "not_installed"})
        raw = self._call_model(prompt)

        # 1) Try strict JSON extraction and manual validation (avoid pydantic validation here)
        json_match = re.search(r"\{[\s\S]*\}", raw)
        if json_match:
            raw_json = json_match.group()
            try:
                parsed = json.loads(raw_json)
            except json.JSONDecodeError:
                parsed = None

            if isinstance(parsed, dict):
                code = parsed.get("code")
                language = parsed.get("language") or (self._detect_language(str(code)) if code else self._detect_language(raw))
                confidence = parsed.get("confidence")

                def _join_code_values(cd: dict) -> str:
                    parts = []
                    for v in cd.values():
                        if isinstance(v, str):
                            parts.append(v)
                        elif isinstance(v, dict):
                            for key in ("content", "code", "body", "text"):
                                if key in v and isinstance(v[key], str):
                                    parts.append(v[key])
                                    break
                            else:
                                parts.append(json.dumps(v))
                        else:
                            parts.append(str(v))
                    return "\n\n".join(parts)

                actions = []
                if isinstance(code, dict):
                    main_code = _join_code_values(code)
                    actions.append(ExecutionAction(type="run_code", language=language, code=main_code))
                elif isinstance(code, str):
                    actions.append(ExecutionAction(type="run_code", language=language, code=code))

                if actions:
                    return ExecutionResult(
                        status="ok",
                        final=True,
                        language=language,
                        code=code,
                        actions=actions,
                        output=None,
                        metadata={"confidence": confidence},
                    )

        # 2) look for triple-backtick code blocks ```lang\n...```
        m = re.search(r"```(?:([a-zA-Z0-9_+-]+)\n)?([\s\S]*?)```", raw)
        if m:
            lang = m.group(1) or self._detect_language(m.group(2))
            code_snip = m.group(2)
            return ExecutionResult(
                status="ok",
                final=True,
                language=lang,
                code=code_snip,
                actions=[ExecutionAction(type="run_code", language=lang, code=code_snip)],
                output=None,
                metadata={"confidence": None, "fallback": "code_block"},
            )

        # 3) try to extract a JSON value for key "code": which may be string or object
        m2 = re.search(r'"code"\s*:\s*("(?:\\.|[^\"])*"|\{[\s\S]*?\})', raw)
        if m2:
            raw_code = m2.group(1)
            if raw_code.strip().startswith("{"):
                try:
                    code_val = json.loads(raw_code)
                    if isinstance(code_val, dict):
                        # reuse robust join logic
                        def _join_code_values(cd: dict) -> str:
                            parts = []
                            for v in cd.values():
                                if isinstance(v, str):
                                    parts.append(v)
                                elif isinstance(v, dict):
                                    for key in ("content", "code", "body", "text"):
                                        if key in v and isinstance(v[key], str):
                                            parts.append(v[key])
                                            break
                                    else:
                                        parts.append(json.dumps(v))
                                else:
                                    parts.append(str(v))
                            return "\n\n".join(parts)

                        main_code = _join_code_values(code_val)
                        lang = self._detect_language(main_code)
                        return ExecutionResult(
                            status="ok",
                            final=True,
                            language=lang,
                            code=code_val,
                            actions=[ExecutionAction(type="run_code", language=lang, code=main_code)],
                            output=None,
                            metadata={"confidence": None, "fallback": "code_field"},
                        )
                except json.JSONDecodeError:
                    pass
            else:
                s = raw_code
                if s.startswith('"') and s.endswith('"'):
                    s = s[1:-1]
                s = s.encode('utf-8').decode('unicode_escape')
                lang = self._detect_language(s)
                return ExecutionResult(
                    status="ok",
                    final=True,
                    language=lang,
                    code=s,
                    actions=[ExecutionAction(type="run_code", language=lang, code=s)],
                    output=None,
                    metadata={"confidence": None, "fallback": "code_field"},
                )

        # 4) fallback: no sensible code found — return informative error result
        short_raw = raw if len(raw) <= 1000 else raw[:1000] + "..."
        return ExecutionResult(
            status="error",
            final=True,
            output=f"ollama: parse_error: could not extract code from model output: {short_raw}",
            metadata={"raw": raw[:2000], "error": "parse_error"},
        )


class OllamaProvider(IntelligenceProvider):
    """Ollama provider implementation."""

    def initialize(self, config):
        """Initialize provider with config."""
        from ..intelligence import IntelligenceConfig

        self.config = config
        model = getattr(config, "model", None) or "qwen2.5-coder:3b"
        self.client = CopilotClient(model=model)

    def invoke(self, messages, context):
        """Invoke model and return ExecutionResult."""
        question = messages[-1]["content"] if messages else ""
        # Delegate to client which returns an ExecutionResult (no broad try/except)
        return self.client.ask_execution(question)

    async def train(self, data, config):
        """Train or fine-tune model (noop PoC)."""
        return True

    def embed(self, items):
        """Return placeholder embeddings."""
        return [[0.0] * 128 for _ in items]

    def cleanup(self):
        """Cleanup resources."""
        pass


# Register Ollama provider if registry available
try:
    from ..intelligence import get_provider_registry

    get_provider_registry().register("ollama", OllamaProvider)
except Exception:
    pass
