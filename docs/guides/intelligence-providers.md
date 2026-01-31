# Intelligence Provider Implementation Guide

Este guia apresenta **passo a passo** como implementar novos provedores de IA em Corplang. A mesma abordagem aplicada ao sistema de Migrations Multi-Driver será usada aqui.

## Visão Geral

Um `IntelligenceProvider` é um contrato abstrato que Corplang usa para comunicar com backends de IA (LLM). Você pode:

- Implementar **LiteLLM** para suportar 100+ modelos (OpenAI, Anthropic, Hugging Face, etc.)
- Implementar **Ollama** para LLMs locais
- Implementar **Claude 3** ou **Gemini** diretamente
- Implementar provedores **customizados** (sua empresa, sua arquitetura)

---

## Arquitetura: Provider Contract

### Interface Base

```python
# runtime/intelligence.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class IntelligenceConfig:
    """Configuração abstrata de provider."""
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout_seconds: int = 30
    extra: Dict[str, Any] = None  # Provider-specific config

class Message:
    """Estrutura de mensagem."""
    def __init__(self, role: str, content: str):
        self.role = role      # "user", "assistant", "system"
        self.content = content

class IntelligenceProvider(ABC):
    """Abstract contract para todos os provedores."""
    
    @abstractmethod
    def initialize(self, config: IntelligenceConfig) -> None:
        """Setup: Valide configuração, carregue modelos, etc."""
        pass
    
    @abstractmethod
    def invoke(self, messages: List[Message], context: Dict) -> str:
        """Invoke: Processe mensagens e retorne resposta."""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Embed (opcional): Gere embedding para texto."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Health check: Verifique se provider está disponível."""
        pass
```

### Registry Pattern

```python
# runtime/intelligence.py

class ProviderRegistry:
    """Registry para instanciar providers by name."""
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type) -> None:
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, name: str, config: IntelligenceConfig) -> IntelligenceProvider:
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        return cls._providers[name]().initialize(config)

# Global registry instance
_registry = ProviderRegistry()

def get_provider_registry() -> ProviderRegistry:
    return _registry
```

---

## Exemplo 1: Ollama (Local LLM)

### Passo 1: Definir Classe

Crie `runtime/providers/ollama_provider.py`:

```python
import requests
from typing import List, Dict, Optional
from runtime.intelligence import IntelligenceProvider, IntelligenceConfig, Message

class OllamaProvider(IntelligenceProvider):
    """Provider para Ollama (LLM local)."""
    
    def __init__(self):
        self.config: Optional[IntelligenceConfig] = None
        self.base_url: str = "http://localhost:11434"
        self.conversation_history: List[Message] = []
    
    def initialize(self, config: IntelligenceConfig) -> 'OllamaProvider':
        """Valide configuração e teste conexão."""
        self.config = config
        
        # Extraia base_url de extra se fornecido
        if config.extra and "base_url" in config.extra:
            self.base_url = config.extra["base_url"]
        
        # Teste conexão
        if not self.is_available():
            raise ConnectionError(f"Ollama unavailable at {self.base_url}")
        
        return self
    
    def is_available(self) -> bool:
        """Verifique se Ollama está rodando."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def invoke(self, messages: List[Message], context: Dict) -> str:
        """Chame Ollama API."""
        # Prepare mensagens
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Mantenha histórico
        self.conversation_history.extend(messages)
        
        # Chame API
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.config.model,
                "messages": formatted_messages,
                "temperature": self.config.temperature,
                "stream": False
            },
            timeout=self.config.timeout_seconds
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Ollama error: {response.text}")
        
        result = response.json()["message"]["content"]
        
        # Adicione resposta ao histórico
        self.conversation_history.append(
            Message("assistant", result)
        )
        
        return result
    
    def embed(self, text: str) -> List[float]:
        """Gere embedding usando Ollama."""
        response = requests.post(
            f"{self.base_url}/api/embed",
            json={
                "model": self.config.model,
                "input": text
            },
            timeout=self.config.timeout_seconds
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Ollama embed error: {response.text}")
        
        return response.json()["embeddings"][0]
```

### Passo 2: Registrar Provider

Em `runtime/intelligence.py`, adicione:

```python
from runtime.providers.ollama_provider import OllamaProvider

# Registre ao inicializar o módulo
get_provider_registry().register("ollama", OllamaProvider)
```

### Passo 3: Usar em Corplang

```mp
agent MyAgent {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.7,
    "base_url": "http://localhost:11434"
  }
  
  fn processar(prompt: text) -> text {
    return invoke self with prompt
  }
}
```

---

## Exemplo 2: LiteLLM (Multi-Model)

### Passo 1: Definir Classe

Crie `runtime/providers/litellm_provider.py`:

```python
import litellm
from typing import List, Dict, Optional
from runtime.intelligence import IntelligenceProvider, IntelligenceConfig, Message

class LiteLLMProvider(IntelligenceProvider):
    """Provider usando LiteLLM — suporta 100+ modelos."""
    
    def __init__(self):
        self.config: Optional[IntelligenceConfig] = None
        self.conversation_history: List[Message] = []
    
    def initialize(self, config: IntelligenceConfig) -> 'LiteLLMProvider':
        """Valide API key e teste conexão."""
        self.config = config
        
        # API key deve vir de variável de ambiente
        # Ex: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
        
        # Teste conexão com chamada mínima
        if not self.is_available():
            raise ConnectionError(f"LiteLLM model unavailable: {config.model}")
        
        return self
    
    def is_available(self) -> bool:
        """Teste se modelo é acessível."""
        try:
            # Chamada rápida de teste
            response = litellm.completion(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
                timeout=5
            )
            return True
        except:
            return False
    
    def invoke(self, messages: List[Message], context: Dict) -> str:
        """Chame modelo via LiteLLM."""
        # Prepare mensagens
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Mantenha histórico
        self.conversation_history.extend(messages)
        
        # Chame LiteLLM
        response = litellm.completion(
            model=self.config.model,
            messages=formatted_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout_seconds
        )
        
        result = response.choices[0].message.content
        
        # Adicione resposta ao histórico
        self.conversation_history.append(
            Message("assistant", result)
        )
        
        return result
    
    def embed(self, text: str) -> List[float]:
        """Gere embedding."""
        response = litellm.embedding(
            model="text-embedding-ada-002",  # Customize
            input=[text]
        )
        return response.data[0]["embedding"]
```

### Passo 2: Registrar

```python
from runtime.providers.litellm_provider import LiteLLMProvider

get_provider_registry().register("litellm", LiteLLMProvider)
```

### Passo 3: Usar

```mp
# Suporta OpenAI
agent GPTAgent {
  config: {
    "provider": "litellm",
    "model": "gpt-4"
  }
  fn processar(prompt: text) -> text { return invoke self with prompt }
}

# Suporta Anthropic
agent ClaudeAgent {
  config: {
    "provider": "litellm",
    "model": "claude-3-opus-20240229"
  }
  fn processar(prompt: text) -> text { return invoke self with prompt }
}

# Suporta Hugging Face
agent HFAgent {
  config: {
    "provider": "litellm",
    "model": "huggingface/mistral-7b-instruct-v0-1"
  }
  fn processar(prompt: text) -> text { return invoke self with prompt }
}
```

---

## Exemplo 3: Custom Provider (Sua Empresa)

Imagine você tem um **serviço interno de IA** que você quer expor via Corplang:

### Passo 1: Definir Classe

```python
# runtime/providers/internal_ai_provider.py

import requests
from runtime.intelligence import IntelligenceProvider, IntelligenceConfig, Message
from typing import List, Dict

class InternalAIProvider(IntelligenceProvider):
    """Provider customizado para serviço IA interno."""
    
    def __init__(self):
        self.config: Optional[IntelligenceConfig] = None
        self.internal_api_url: str = None
        self.api_key: str = None
    
    def initialize(self, config: IntelligenceConfig) -> 'InternalAIProvider':
        """Setup para serviço interno."""
        self.config = config
        
        # Extraia URL e chave
        if not config.extra or "internal_url" not in config.extra:
            raise ValueError("internal_url required in config.extra")
        
        self.internal_api_url = config.extra["internal_url"]
        self.api_key = config.extra.get("api_key", "")
        
        if not self.is_available():
            raise ConnectionError(f"Internal AI service unavailable at {self.internal_api_url}")
        
        return self
    
    def is_available(self) -> bool:
        """Health check ao serviço interno."""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"{self.internal_api_url}/health",
                headers=headers,
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def invoke(self, messages: List[Message], context: Dict) -> str:
        """Invoke serviço interno."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Adapte formato para seu serviço interno
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": m.role, "content": m.content}
                for m in messages
            ],
            "parameters": {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                # Adicione qualquer parâmetro customizado
                "department": context.get("department"),
                "user_id": context.get("user_id")
            }
        }
        
        response = requests.post(
            f"{self.internal_api_url}/invoke",
            json=payload,
            headers=headers,
            timeout=self.config.timeout_seconds
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Internal AI error: {response.text}")
        
        return response.json()["result"]
    
    def embed(self, text: str) -> List[float]:
        """Embedding via serviço interno."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.post(
            f"{self.internal_api_url}/embed",
            json={"text": text},
            headers=headers,
            timeout=self.config.timeout_seconds
        )
        
        return response.json()["embedding"]
```

### Passo 2: Registrar

```python
from runtime.providers.internal_ai_provider import InternalAIProvider

get_provider_registry().register("internal", InternalAIProvider)
```

### Passo 3: Usar

```mp
agent CorporateAgent {
  config: {
    "provider": "internal",
    "model": "corporate-gpt-v2",
    "internal_url": "https://ai-service.company.internal",
    "api_key": "${INTERNAL_AI_KEY}"
  }
  
  fn processar(pergunta: text, departamento: text) -> text {
    # context passa departamento e user_id automaticamente
    return invoke self with pergunta
  }
}
```

---

## Ciclo de Vida: Como Corplang Usa Providers

```
┌─────────────────────────────────────┐
│ Código Corplang                     │
│                                     │
│ agent MyAgent { config: { ... } }   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ PARSE: AgentDefinition AST node     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ AgentManager.create_agent(node)     │
│ • Extrai config                     │
│ • Armazena em AgentState            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ invoke self with prompt             │
│ • AgentManager.get_agent(name)      │
│ • AgentManager.predict_agent()      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ ProviderRegistry.create()           │
│ • Lookup provider by name           │
│ • Instanciar se primeira vez       │
│ • Cache resultado em AgentState     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ IntelligenceProvider.invoke()       │
│ • Prepare mensagens                 │
│ • Chamar backend (Ollama/OpenAI)   │
│ • Retorna resposta                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ AgentState.provider_state           │
│ • Salva histórico de mensagens      │
│ • Atualiza metadata                 │
│ • Sem recompilar AST                │
└─────────────────────────────────────┘
```

---

## Padrão: State & Context

Cada provider tem acesso a **contexto**:

```python
def invoke(self, messages: List[Message], context: Dict) -> str:
    """context contém:
    - agent_name: str
    - execution_count: int
    - user_id: Optional[str]
    - department: Optional[str]
    - custom fields: Dict[str, Any]
    """
    pass
```

Use contexto para **personalizar comportamento**:

```python
class ContextAwareProvider(IntelligenceProvider):
    def invoke(self, messages: List[Message], context: Dict) -> str:
        # Customize baseado em user_id
        user_id = context.get("user_id")
        if user_id == "admin":
            self.config.temperature = 0.1  # Mais determinístico
        else:
            self.config.temperature = 0.7  # Mais criativo
        
        return litellm.completion(...)
```

---

## Checklist: Implementar Novo Provider

- [ ] Herde de `IntelligenceProvider`
- [ ] Implemente `initialize(config) -> self`
- [ ] Implemente `invoke(messages, context) -> str`
- [ ] Implemente `embed(text) -> List[float]`
- [ ] Implemente `is_available() -> bool`
- [ ] Teste conexão em `initialize()`
- [ ] Mantenha histórico de mensagens
- [ ] Registre em `ProviderRegistry`
- [ ] Adicione testes unitários
- [ ] Documente em `language_config.yaml`

---

## Testes Unitários

Exemplo:

```python
# runtime/tests/test_ollama_provider.py

import pytest
from runtime.providers.ollama_provider import OllamaProvider
from runtime.intelligence import IntelligenceConfig, Message

class TestOllamaProvider:
    
    @pytest.fixture
    def provider(self):
        config = IntelligenceConfig(
            provider="ollama",
            model="llama2",
            temperature=0.7
        )
        return OllamaProvider().initialize(config)
    
    def test_is_available(self, provider):
        # Skip if Ollama not running
        if not provider.is_available():
            pytest.skip("Ollama not available")
        assert provider.is_available()
    
    def test_invoke(self, provider):
        if not provider.is_available():
            pytest.skip("Ollama not available")
        
        messages = [Message("user", "Hello")]
        result = provider.invoke(messages, {})
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_conversation_history(self, provider):
        messages1 = [Message("user", "What is 2+2?")]
        result1 = provider.invoke(messages1, {})
        
        messages2 = [Message("user", "And 3+3?")]
        result2 = provider.invoke(messages2, {})
        
        # Histórico deve ter ambas as mensagens
        assert len(provider.conversation_history) >= 4
```

---

## Integração com Language Config

Seu provider agora é acessível via `language_config.yaml`:

```yaml
corplang:
  version: "0.1.0"
  name: "meu_projeto"

intelligence:
  # Provider padrão
  provider: "ollama"
  config:
    model: "llama2"
    temperature: 0.7
    base_url: "http://localhost:11434"

  # Múltiplos providers (cada agente escolhe)
  available_providers:
    - name: "ollama"
      config:
        model: "llama2"
        base_url: "http://localhost:11434"
    
    - name: "litellm"
      config:
        model: "gpt-4"
        api_key: "${OPENAI_API_KEY}"
    
    - name: "internal"
      config:
        model: "corporate-gpt"
        internal_url: "https://ai.company.internal"
        api_key: "${INTERNAL_API_KEY}"
```

---

## Próximas Etapas

1. **Observabilidade**: Como rastrear latência de cada provider?
   → [Observabilidade Avançada](observability.md)

2. **Caching**: Como evitar chamar o mesmo provider múltiplas vezes?
   → [Estratégia de Cache](caching.md)

3. **Tool Calling**: Como dar "ferramentas" ao agente?
   → [Tool Calling / Function Calling](tool-calling.md)

---

## Referência Rápida

| Método | Responsabilidade | Retorno |
|--------|------------------|---------|
| `initialize(config)` | Setup e validação | `self` |
| `invoke(messages, context)` | Chamar backend IA | `str` (resposta) |
| `embed(text)` | Gerar embedding | `List[float]` |
| `is_available()` | Health check | `bool` |

---

## Suporte

- Perguntas? Abra uma issue no GitHub
- Quer compartilhar seu provider? Faça um PR!
- Documentação: [runtime_architecture.md](../runtime_architecture.md)
