# Secure Incidents Tracker

[![CI](https://github.com/Vicfvieira/secure-incidents-tracker-/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Vicfvieira/secure-incidents-tracker-/actions/workflows/ci.yml)

Aplicação full stack para registro, gestão e auditoria de incidentes de
segurança da informação (phishing, vazamento de dados, malware, etc.),
voltada para times de resposta a incidentes (Blue Team).

## Tecnologias

- **Backend:** Python 3.11 + FastAPI
- **Frontend:** React (Vite)
- **Banco de Dados:** PostgreSQL
- **ORM/Migrations:** SQLAlchemy 2.0 + Alembic
- **Autenticação:** JWT com RBAC (controle de acesso baseado em papéis)
- **Documentação:** OpenAPI 3.0 / Swagger UI (`/api/v1/docs`)

## Regras de negócio implementadas

### RBAC
| Papel      | Permissões |
|------------|------------|
| `ADMIN`    | Tudo que `ANALYST` pode, mais: deletar incidentes, gerenciar usuários |
| `ANALYST`  | Criar, listar, ler e atualizar status/severidade de qualquer incidente; ler a trilha de auditoria |
| `REPORTER` | Criar incidentes; listar e ler apenas os incidentes que reportou |

### Severidade e status
- Severidade: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- Status: `OPEN`, `INVESTIGATING`, `MITIGATED`, `RESOLVED`, `CLOSED`

### Trilha de auditoria (audit trail)
Toda alteração de `status` ou `severity` de um incidente gera automaticamente
um registro imutável na tabela `incident_logs`, contendo o ID do incidente,
o usuário que alterou, o valor antigo, o valor novo e o timestamp. Ver
`app/crud/incident.py::update_incident`.

### Criptografia em repouso (field-level encryption)
Os campos `description` e `indicators` (indicadores de comprometimento / IoCs)
de cada incidente são criptografados de forma transparente com Fernet
(AES-128-CBC + HMAC) antes de serem gravados no PostgreSQL, e descriptografados
automaticamente ao serem lidos pela aplicação. Ver `app/core/encryption.py`.

## Endpoints principais

| Método | Endpoint | Papéis | Descrição |
|--------|----------|--------|-----------|
| POST | `/api/v1/auth/register` | público | Cria uma conta (o primeiro usuário do sistema vira `ADMIN` automaticamente) |
| POST | `/api/v1/auth/login` | público | Retorna um JWT (limitado a 5 tentativas/minuto por IP) |
| POST | `/api/v1/incidents` | qualquer autenticado | Cria um incidente |
| GET | `/api/v1/incidents` | qualquer autenticado | Lista incidentes de forma paginada (REPORTER vê apenas os seus) |
| GET | `/api/v1/incidents/{id}` | qualquer autenticado | Detalhe de um incidente |
| PATCH | `/api/v1/incidents/{id}` | ANALYST, ADMIN | Atualiza `status`/`severity` (gera log de auditoria) |
| DELETE | `/api/v1/incidents/{id}` | ADMIN | Remove um incidente |
| GET | `/api/v1/incidents/{id}/logs` | ANALYST, ADMIN | Trilha de auditoria do incidente |
| GET | `/api/v1/users/me` | qualquer autenticado | Dados do usuário logado |
| GET | `/api/v1/users` | ADMIN | Lista usuários |
| POST | `/api/v1/users` | ADMIN | Cria um usuário com papel específico |

#### Paginação e filtros em `GET /api/v1/incidents`

Query params opcionais:

| Param | Padrão | Limite | Descrição |
|-------|--------|--------|-----------|
| `page` | `1` | mínimo `1` | Página desejada |
| `limit` | `20` | máximo `100` | Itens por página |
| `severity` | — | `LOW`\|`MEDIUM`\|`HIGH`\|`CRITICAL` | Filtra por severidade |
| `status` | — | `OPEN`\|`INVESTIGATING`\|`MITIGATED`\|`RESOLVED`\|`CLOSED` | Filtra por status |

A resposta traz `items`, `total`, `page`, `limit` e `total_pages`:

```json
{
  "items": [ ... ],
  "total": 42,
  "page": 1,
  "limit": 20,
  "total_pages": 3
}
```

### Exemplo — criar incidente

```json
POST /api/v1/incidents
{
  "title": "Suspeita de Phishing no RH",
  "description": "E-mail com anexo malicioso enviado para o setor de RH. Contém dados de funcionários.",
  "severity": "HIGH",
  "type": "PHISHING",
  "indicators": ["malicious-link.com", "192.168.1.50"]
}
```

## Rodando localmente

### Com Docker Compose (backend + frontend + banco)

```bash
cp .env.example .env
# edite JWT_SECRET_KEY e FIELD_ENCRYPTION_KEY em .env
docker compose up --build
```

- API em `http://localhost:8000` (Swagger em `http://localhost:8000/api/v1/docs`)
- Frontend em `http://localhost:4173`

### Backend sem Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite .env com sua string de conexão do PostgreSQL, JWT_SECRET_KEY
# e FIELD_ENCRYPTION_KEY (gere uma chave com o comando abaixo)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend

Frontend mínimo em React (Vite) que consome a API: tela de login/cadastro,
lista de incidentes com filtros por severidade e status (badge colorido por
severidade), formulário de criação de incidente e um gráfico de incidentes
por severidade (Recharts).

```bash
cd frontend
cp .env.example .env
# edite VITE_API_BASE_URL se a API não estiver em http://localhost:8000/api/v1
npm install
npm run dev
```

A aplicação sobe em `http://localhost:5173`. Como o backend não expõe um
endpoint de registro de usuários fora do bootstrap (o primeiro usuário
cadastrado vira `ADMIN` automaticamente), a própria tela de login permite
criar uma conta ("Não tem conta? Criar uma agora").

## Testes

```bash
pip install -r requirements.txt
pytest
```

A suíte de testes roda contra um banco SQLite em memória (via
`tests/conftest.py`) e cobre autenticação, RBAC, CRUD de incidentes,
geração da trilha de auditoria e criptografia em repouso.

## Estrutura do projeto

```
app/
  api/v1/        # routers (auth, incidents, users)
  core/          # segurança (JWT/bcrypt) e criptografia de campos
  crud/          # regras de acesso a dados
  models/        # modelos SQLAlchemy (User, Incident, IncidentLog)
  schemas/       # schemas Pydantic (request/response)
  config.py      # configurações via variáveis de ambiente
  database.py    # engine/sessão SQLAlchemy
  deps.py        # dependências de autenticação/RBAC
  main.py        # instância FastAPI e montagem dos routers
alembic/         # migrations
tests/           # suíte pytest
frontend/        # aplicação React (Vite) que consome a API
```

## Contexto de Segurança

Projeto educacional, desenvolvido para estudo de boas práticas em segurança
da informação e AppSec (autenticação JWT, RBAC, trilha de auditoria imutável
e criptografia de dados sensíveis em repouso).
