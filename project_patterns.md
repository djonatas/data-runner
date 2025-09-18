````markdown
# Padrões de Código do Projeto (Python)

Este documento define os **padrões de codificação** e as **boas práticas** para projetos em **Python**, com foco em **FastAPI**, **Type Hints**, **Testes** e **REST/HTTP**. Todas as regras são **obrigatórias** e servem como base para qualquer novo projeto.

---

## 1. Python / Tipagem / Organização do Código

- Todo o código-fonte deve ser escrito para **Python 3.12+** com **type hints** completos.
- Use **Poetry** como gerenciador de dependências e scripts (`pyproject.toml`).
- Estilo e qualidade:
  - **Black** para formatação, **isort** para ordenação de imports, **Ruff** para lint, **mypy** para checagem de tipos.
  - Ativar `mypy --strict` em módulos de domínio (permitido relaxar em camadas de borda com justificativa).
- Evitar variáveis mutáveis globais. Preferir **funções puras** e **imutabilidade** sempre que possível.
- Usar **dataclasses** ou **Pydantic** para estruturas de dados.
- **Nunca** usar `Any` sem justificativa documentada. Prefira `Protocol`, `TypedDict` ou `Generic` quando necessário.
- Preferir **compreensões** e funções como `map/filter` com parcimônia; priorizar legibilidade.
- Usar **async/await** (FastAPI assíncrono) e lib **httpx** para I/O externo.
- Módulos com exportações claras (evitar `from x import *`).
- Evitar **circular dependencies** com camadas bem definidas (domain ⇄ app ⇄ infra).
- Nomear módulos, pacotes e variáveis em **snake_case**; classes em **PascalCase**; constantes em **UPPER_SNAKE**.

## 2. Configuração e Variáveis de Ambiente

- Usar **pydantic-settings** (v2) global com validação.
- Exigir convenção por ambiente: `.env.development`, `.env.test`, `.env.production`.
- Variáveis mínimas: `ENV`, `PORT`, `DATABASE_URL` (quando aplicável).
- O build deve **falhar** se a validação de env falhar.

Exemplo (settings):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='forbid')

    ENV: str
    PORT: int = 8000
    DATABASE_URL: str | None = None

settings = Settings()
```
````

---

## 3. Logs e Correlação (request-id)

- Injetar **`X-Request-ID`** (middleware) e retornar no header da resposta.
- Logger **estruturado** com `structlog` (ou `logging` com `jsonlogger`).
- Padrão de logs: nível, timestamp, método, caminho, status, duração, `request_id`.

Exemplo (middleware simples):

```python
import time, uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.perf_counter()
        response: Response = await call_next(request)
        response.headers["x-request-id"] = rid
        response.headers["x-response-time-ms"] = f"{(time.perf_counter()-start)*1000:.2f}"
        return response
```

---

## 4. Tratamento de Erros

- Padronizar erros com **handlers globais** que retornam o **envelope** de resposta.
- Ma
  Envelope e helpers (genérico):

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiError(BaseModel):
    code: str
    message: str
    field: str | None = None

class Meta(BaseModel):
    total: int | None = None
    page: int | None = None
    pageSize: int | None = None
    cursor: str | None = None

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    statusCode: int
    message: str | None = None
    data: T | None = None
    errors: list[ApiError] | None = None
    meta: Meta | None = None
    requestId: str | None = None

def ok(data: T, message: str = "OK", status_code: int = 200) -> ApiResponse[T]:
    return ApiResponse(success=True, statusCode=status_code, message=message, data=data)

def fail(status_code: int, message: str, errors: list[ApiError] | None = None) -> ApiResponse[None]:
    return ApiResponse(success=False, statusCode=status_code, message=message, errors=errors, data=None)
```

## 5. Banco de Dados

- ORM: **SQLAlchemy 2.0** (async) + **Alembic** para migrações. (Alternativa: **SQLModel** ou **Prisma Client Python** com justificativa.)
- Evitar mudanças destrutivas sem migração planejada e **rollback** definido.
- **Não usar enums nativos** do banco. Preferir `String` e documentar valores aceitos ao lado.  
  Ex.: `status: Mapped[str]  # "SCHEDULED" | "CONFIRMED" | ...`
- **Identidades compostas** quando necessário para multi-tenant. Ex.: entidades identificadas por `(tenant_id, id)`; `cpf` único por tenant.
- Conexões **assíncronas** (`asyncpg`/`aiosqlite`) e sessão por requisição (dependency FastAPI).

---

## 6. Estrutura do Projeto (sugerida)

```
app/
  core/
    config.py
    logging.py
    errors.py
    security.py
  domain/
    users/
      entities.py
      use_cases.py
      ports.py
  infra/
    db/
      models.py
      session.py
      repositories.py
  __init__.py

tests/
  unit/
  integration/
  e2e/
```

---

## 7. Chamadas Externas / Resiliência

- `httpx` com:
  - **Timeouts** (conexão/leitura/escrita/total)
  - **Retries** com backoff exponencial (tenacity ou httpx.Retry transport)
  - **Circuit breaker** quando crítico (ex.: `aiobreaker`)
- Propagar/gerar `X-Request-ID` em chamadas saindo do serviço.

---

## 8. Padrões de Commit e Branching

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- Branching: `main` (estável), `develop` (integração), feature branches por tarefa.
- PRs exigem revisão e aprovação; CI deve passar antes de merge.

---

## 9. Segurança de Dados e Privacidade

- Não logar dados sensíveis (tokens, senhas, PII). Mascarar quando necessário.
- Criptografar segredos em repouso e **NUNCA** commitar `.env`.
- LGPD/GDPR: coletar o mínimo necessário e documentar base legal.

---
