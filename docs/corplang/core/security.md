# security.py — Sistema de Segurança

Módulo central para autenticação, autorização, rate limiting e controle de IP no interpretador Corplang/MF07.

## Funcionalidades
- Autenticação por token.
- Autorização de ações por usuário.
- Rate limiting por IP.
- Bloqueio e desbloqueio de IPs.

## Exemplo de uso
```python
from src.corplang.core.security import security_manager

security_manager.register_token("user1", "token123")
assert security_manager.authenticate("token123")
assert security_manager.authorize("user1", "run")

ip = "127.0.0.1"
if not security_manager.check_rate_limit(ip):
    print("Rate limit excedido!")
```

## Extensão
- Adicione novos métodos para políticas de segurança customizadas.
- Documente exemplos de integração com agentes e pontos de extensão.
