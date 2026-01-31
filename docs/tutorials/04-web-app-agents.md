# Tutorial 4 — Web App: HTTP Server com Agentes (35 min)

Tudo que você aprendeu — validação com IA, multi-agent routing, persistência — agora vai para **produção** como uma API HTTP.

Em Corplang, você não precisa escolher entre "código que compila rápido" e "código que usa IA". Agentes são tão nativos que você os expõe via HTTP sem camadas de abstração.

## O Que Você Aprenderá

- Criar servidor HTTP nativo: `serve http { }`
- Rotear requisições a agentes especializados
- Validar payload automaticamente
- Tratamento de erro profissional
- Logging e observabilidade distribuída

## Pré-requisitos

- Completar [Tutorial 3](03-ai-validated-persistence.md)
- Porta 8000 disponível (ou customize)
- Provider configurado

---

## Parte 1: Servidor HTTP Básico (10 min)

### Criar Projeto

```bash
mf init sentiment-api
cd sentiment-api
```

### Código: `main.mp`

```mp
# Agente: Classifica sentimento
agent AnalisadorSentimento {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.3
  }
  
  fn analisar(texto: text) -> text {
    let prompt = """
    Analise o sentimento deste texto e responda com:
    POSITIVO | NEUTRO | NEGATIVO
    
    Texto: {texto}
    """
    return invoke self with prompt
  }
  
  fn calcular_score(texto: text) -> int {
    let prompt = """
    Dê um score de 1-10 para o sentimento deste texto.
    Responda APENAS com um número de 1 a 10.
    
    Texto: {texto}
    """
    let resultado = invoke self with prompt
    # Parse do resultado
    return int.parse(resultado)
  }
}

# Agente: Valida entrada
agent ValidadorTexto {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.1
  }
  
  fn validar(texto: text) -> bool {
    # Validações básicas
    if text.length(texto) == 0 {
      return false
    }
    if text.length(texto) > 5000 {
      return false
    }
    # Mais validações podem vir do agente
    return true
  }
}

# Modelo: Resultado de análise
model SentimentResult {
  id: int primary_key auto_increment
  texto: text not_null
  sentimento: text
  score: int
  criado_em: datetime auto_now
}

# Persistência: Salva resultados
driver ResultadoRepository {
  fn salvar(resultado: SentimentResult) -> bool
  fn listar_ultimos(limite: int) -> [SentimentResult]
  fn buscar(id: int) -> SentimentResult
}

impl ResultadoRepository for SQLiteDriver {
  fn salvar(resultado: SentimentResult) -> bool {
    try {
      insert into SentimentResult (texto, sentimento, score)
      values (resultado.texto, resultado.sentimento, resultado.score)
      return true
    } catch (e: Exception) {
      println("Erro ao salvar: " + e.message)
      return false
    }
  }
  
  fn listar_ultimos(limite: int) -> [SentimentResult] {
    return select * from SentimentResult order by criado_em desc limit limite
  }
  
  fn buscar(id: int) -> SentimentResult {
    return select * from SentimentResult where id = id limit 1
  }
}

# Modelo: Requisição JSON
type AnaliseRequest {
  texto: text
}

# Modelo: Resposta JSON
type AnaliseResponse {
  sucesso: bool
  mensagem: text
  dados: {
    sentimento: text,
    score: int,
    id: int
  } | null
}

# Handler: POST /analisar
fn handle_analisar(request: http.Request) -> http.Response {
  # 1. PARSE JSON
  var payload: AnaliseRequest
  try {
    payload = json.parse(request.body) as AnaliseRequest
  } catch (e: Exception) {
    let resposta = AnaliseResponse {
      sucesso: false,
      mensagem: "JSON inválido: " + e.message,
      dados: null
    }
    return http.Response {
      status: 400,
      body: json.stringify(resposta)
    }
  }
  
  # 2. VALIDAR
  let validador = new ValidadorTexto()
  if !validador.validar(payload.texto) {
    let resposta = AnaliseResponse {
      sucesso: false,
      mensagem: "Texto vazio ou muito longo (máximo 5000 caracteres)",
      dados: null
    }
    return http.Response {
      status: 400,
      body: json.stringify(resposta)
    }
  }
  
  # 3. ANALISAR COM AGENTE
  let analisador = new AnalisadorSentimento()
  var sentimento: text
  var score: int
  
  try {
    sentimento = analisador.analisar(payload.texto)
    score = analisador.calcular_score(payload.texto)
  } catch (e: Exception) {
    let resposta = AnaliseResponse {
      sucesso: false,
      mensagem: "Erro ao processar: " + e.message,
      dados: null
    }
    return http.Response {
      status: 500,
      body: json.stringify(resposta)
    }
  }
  
  # 4. SALVAR RESULTADO
  let repo = new ResultadoRepository()
  var resultado = SentimentResult {
    texto: payload.texto,
    sentimento: sentimento,
    score: score
  }
  
  let sucesso = repo.salvar(resultado)
  if !sucesso {
    let resposta = AnaliseResponse {
      sucesso: false,
      mensagem: "Erro ao salvar resultado",
      dados: null
    }
    return http.Response {
      status: 500,
      body: json.stringify(resposta)
    }
  }
  
  # 5. RETORNAR SUCESSO
  let resposta = AnaliseResponse {
    sucesso: true,
    mensagem: "Análise concluída",
    dados: {
      sentimento: sentimento,
      score: score,
      id: resultado.id
    }
  }
  
  return http.Response {
    status: 200,
    headers: {
      "Content-Type": "application/json"
    },
    body: json.stringify(resposta)
  }
}

# Handler: GET /ultimos?limite=10
fn handle_ultimos(request: http.Request) -> http.Response {
  let limite = request.query.get("limite", "10")
  let limite_int = int.parse(limite)
  
  let repo = new ResultadoRepository()
  let resultados = repo.listar_ultimos(limite_int)
  
  return http.Response {
    status: 200,
    headers: { "Content-Type": "application/json" },
    body: json.stringify(resultados)
  }
}

# Servidor HTTP
serve http on port 8000 {
  route "POST /analisar" -> handle_analisar
  route "GET /ultimos" -> handle_ultimos
  
  # Health check
  route "GET /health" -> fn(req) {
    return http.Response {
      status: 200,
      body: "{\"status\": \"ok\"}"
    }
  }
}
```

---

## Parte 2: Testar Servidor (8 min)

### Executar

```bash
mf run main.mp
```

Output:

```
[INFO] Server listening on http://localhost:8000
[INFO] Routes registered:
  POST /analisar
  GET /ultimos
  GET /health
```

### Teste 1: Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{"status": "ok"}
```

### Teste 2: Análise de Sentimento

```bash
curl -X POST http://localhost:8000/analisar \
  -H "Content-Type: application/json" \
  -d '{"texto": "Adorei esse produto! Muito bom."}'
```

Response:

```json
{
  "sucesso": true,
  "mensagem": "Análise concluída",
  "dados": {
    "sentimento": "POSITIVO",
    "score": 9,
    "id": 1
  }
}
```

### Teste 3: Listar Análises

```bash
curl "http://localhost:8000/ultimos?limite=5"
```

Response:

```json
[
  {
    "id": 1,
    "texto": "Adorei esse produto! Muito bom.",
    "sentimento": "POSITIVO",
    "score": 9,
    "criado_em": "2025-01-11T10:30:45Z"
  }
]
```

### Teste 4: Erro de Validação

```bash
curl -X POST http://localhost:8000/analisar \
  -H "Content-Type: application/json" \
  -d '{"texto": ""}'
```

Response (400):

```json
{
  "sucesso": false,
  "mensagem": "Texto vazio ou muito longo (máximo 5000 caracteres)",
  "dados": null
}
```

---

## Parte 3: Tratamento Profissional de Erro (8 min)

### Implementar Retry com Backoff

```mp
fn analisar_com_retry(texto: text, max_tentativas: int = 3) -> text {
  var tentativa = 0
  var delay_ms = 100
  
  while tentativa < max_tentativas {
    try {
      let analisador = new AnalisadorSentimento()
      return analisador.analisar(texto)
    } catch (e: Exception) {
      tentativa = tentativa + 1
      if tentativa < max_tentativas {
        println("[Retry " + tentativa + "] Aguardando " + delay_ms + "ms...")
        sys.sleep(delay_ms)
        delay_ms = delay_ms * 2  # Exponential backoff
      } else {
        throw e
      }
    }
  }
  return ""
}

fn handle_analisar_resiliente(request: http.Request) -> http.Response {
  # ... parse e validação ...
  
  try {
    sentimento = analisar_com_retry(payload.texto, 3)
    # ... resto do handler ...
  } catch (e: Exception) {
    let resposta = AnaliseResponse {
      sucesso: false,
      mensagem: "Serviço temporariamente indisponível. Tente novamente.",
      dados: null
    }
    return http.Response {
      status: 503,  # Service Unavailable
      body: json.stringify(resposta)
    }
  }
}
```

### Rate Limiting

```mp
var requisicoes_por_ip = {}

fn rate_limit(ip: text) -> bool {
  var count = requisicoes_por_ip.get(ip, 0)
  if count > 100 {  # Max 100 req/min
    return false
  }
  requisicoes_por_ip.set(ip, count + 1)
  return true
}

fn handle_analisar_limitado(request: http.Request) -> http.Response {
  let ip = request.headers.get("X-Forwarded-For", request.remote_addr)
  
  if !rate_limit(ip) {
    return http.Response {
      status: 429,  # Too Many Requests
      body: "{\"erro\": \"Rate limit excedido\"}"
    }
  }
  
  # ... resto do handler ...
}
```

---

## Parte 4: Logging & Observabilidade (7 min)

### Logging Estruturado

```mp
from core.runtime.observability import get_observability_manager

var request_log = []

fn log_requisicao(metodo: text, path: text, status: int, tempo_ms: int) -> void {
  var entrada = {
    "timestamp": sys.now(),
    "metodo": metodo,
    "path": path,
    "status": status,
    "tempo_ms": tempo_ms
  }
  request_log.append(entrada)
  println("[" + metodo + "] " + path + " → " + status + " (" + tempo_ms + "ms)")
}

fn handle_analisar_com_log(request: http.Request) -> http.Response {
  let inicio = sys.now_ms()
  
  # ... processamento ...
  
  let tempo_ms = sys.now_ms() - inicio
  log_requisicao("POST", "/analisar", 200, tempo_ms)
  
  return resposta
}

fn listar_logs() -> void {
  println("=== Request Log ===")
  for (var log in request_log) {
    println(log.timestamp + " " + log.metodo + " " + log.path + " " + log.status)
  }
}
```

### Integração com Observability Manager

```mp
fn rastreador_http(event) -> void {
  if event.node_type == "HTTPRequestHandler" {
    println("[HTTP] " + event.metadata.method + " " + event.metadata.path)
  }
}

fn main() {
  let obs = get_observability_manager()
  obs.register(rastreador_http)
  
  serve http on port 8000 {
    route "POST /analisar" -> handle_analisar_com_log
    # ...
  }
}

main()
```

---

## Parte 5: Escalar para Produção (5 min)

### Docker

Crie `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instale Corplang
RUN curl -fsSL https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/install.sh | bash

# Copie seu código
COPY . .

# Exponha porta
EXPOSE 8000

# Inicie servidor
CMD ["mf", "run", "main.mp"]
```

Build e execute:

```bash
docker build -t sentiment-api .
docker run -p 8000:8000 sentiment-api
```

### CORS & Headers de Segurança

```mp
fn adicionar_headers_seguranca(response: http.Response) -> http.Response {
  response.headers.set("Access-Control-Allow-Origin", "*")
  response.headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
  response.headers.set("X-Content-Type-Options", "nosniff")
  response.headers.set("X-Frame-Options", "DENY")
  return response
}

fn handle_analisar_seguro(request: http.Request) -> http.Response {
  if request.method == "OPTIONS" {
    return http.Response {
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
      }
    }
  }
  
  let resposta = handle_analisar(request)
  return adicionar_headers_seguranca(resposta)
}
```

### Variáveis de Ambiente

```bash
# .env
OPENAI_API_KEY=sk-...
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=postgresql://user:pass@db:5432/api_db
LOG_LEVEL=info
```

Em `main.mp`:

```mp
fn main() {
  let api_key = sys.env("OPENAI_API_KEY")
  let db_url = sys.env("DATABASE_URL")
  let log_level = sys.env("LOG_LEVEL", "info")
  
  # Configure usando variáveis
  
  serve http on port 8000 {
    # ...
  }
}

main()
```

---

## Arquitetura: Como Funciona

```
┌───────────────────┐
│ Cliente HTTP      │
└────────┬──────────┘
         │ POST /analisar
         │ JSON: {"texto": "..."}
         ▼
┌────────────────────────────────────────┐
│ HTTP Server                            │
│ route "POST /analisar" -> handler      │
└────┬─────────────────────────────────┬─┘
     │                                 │
     ▼                                 ▼
[ValidadorTexto]              [AnalisadorSentimento]
    ↓                              ↓
AgentPredictExecutor         AgentPredictExecutor
    │                              │
    └──────────┬───────────────────┘
               ▼
         [ResultadoRepository]
              │
              ├─→ SQLiteDriver (dev)
              └─→ PostgreSQLDriver (prod)
                     │
                     ▼
               Banco de Dados
```

---

## Checklist para Produção

- [ ] Rate limiting implementado
- [ ] Retry com backoff exponencial
- [ ] Logging estruturado
- [ ] CORS configurado
- [ ] Headers de segurança
- [ ] Variáveis de ambiente setadas
- [ ] Database em PostgreSQL (não SQLite)
- [ ] Migrations testadas
- [ ] Observability integrada
- [ ] Docker image construída

---

## Próximas Etapas

1. **Adicionar autenticação**: Como proteger sua API?
   → [Guia de Autenticação](../guides/authentication.md)

2. **Caching**: Como evitar chamar agentes múltiplas vezes?
   → [Estratégia de Cache](../guides/caching.md)

3. **Monitoramento em produção**: Como saber se tudo está OK?
   → [Observabilidade em Produção](../guides/monitoring.md)

---

**Parabéns!** Você deployou uma API production-ready com agentes IA integrados nativamente. 

Próximo: Explorar a documentação completa e contribuir!
