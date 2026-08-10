# СтудСемья — информационный портал студенческих семей

Веб-приложение для курирования вопросов студенческих семей: статьи о льготах,
выплатах и мерах поддержки, поиск по базе знаний и AI-ассистент (DeepSeek/OpenCode).

## Стек

- **Frontend:** Nuxt 3 (Vue 3, TypeScript, Nuxt UI, Tailwind CSS)
- **Backend:** FastAPI (Python 3.13, SQLAlchemy 2, Alembic, JWT)
  — **независимый посредник** между фронтендом и БД; весь AI-доступ через backend.
- **БД:** SQLite 3 + FTS5 (полнотекстовый поиск) в `data/semyainfo.sqlite`.
  Без Docker и без PostgreSQL.

## Структура проекта

```
docs/          # ТЗ, архитектура, дизайн-референсы (source of truth для UI)
backend/       # FastAPI: app/api, app/services, app/models, app/schemas, alembic, tests
frontend/      # Nuxt: pages, components, composables, shared (types + schemas), tests
```

## Запуск (локальная разработка)

### 1. Backend (FastAPI)

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env      # Windows; при необходимости задайте свои ключи
alembic upgrade head             # применить миграции
python seed.py                   # демо-данные (опционально, но удобно)
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Документация API — http://127.0.0.1:8000/docs

### 2. Frontend (Nuxt)

```
cd frontend
npm install
npm run dev        # http://127.0.0.1:3000
```

Frontend должен обращаться к backend по `NVX_PUBLIC_API_BASE`
(по умолчанию `http://localhost:8000`, см. `frontend/.env.example`).

### Учётные записи по умолчанию (после `seed.py`)

| Роль      | Email                   | Пароль     |
|-----------|-------------------------|------------|
| Админ     | admin@semyainfo.dev     | admin123   |
| Редактор  | editor@semyainfo.dev    | editor123  |

## API (кратко)

- `POST /api/auth/login`, `GET /api/auth/me`, `PATCH /api/auth/me`,
  `POST /api/auth/change-password`, `POST /api/auth/password-recovery`
- `GET /api/articles`, `GET /api/articles/categories`, `GET /api/articles/search`,
  `GET /api/articles/{slug}`
- `POST /api/assistant/chats` … `POST /api/assistant/chats/{id}/messages` (анонимно, session cookie)
- `GET/POST/PATCH/DELETE /api/editor/articles…` (роль `editor`)
- `GET/POST/PATCH/DELETE /api/admin/editors…`, `/api/admin/logs`,
  `/api/admin/ai-settings`, `/api/admin/knowledge…` (роль `admin`)

Роли: `admin` (модератор), `editor` (редактор). Доступ проверяется на backend
в каждом эндпоинте (JWT Bearer).

## Тесты

```
cd backend && .venv\Scripts\python.exe -m pytest tests -q   # 26 тестов
cd frontend && npm run test                                 # 17 тестов (Vitest)
cd frontend && npm run typecheck                            # vue-tsc
cd frontend && npm run build                                # продакшн-сборка
```

## Переменные окружения (backend/.env)

`DATABASE_URL`, `JWT_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
`CORS_ORIGINS` (`http://localhost:3000,http://127.0.0.1:3000`),
`OPENCODE_API_KEY`, `OPENCODE_BASE_URL`, `OPENCODE_MODEL`,
`AI_TEMPERATURE`, `AI_MAX_TOKENS`, `AI_KNOWLEDGE_TOP_K`,
`SEED_ADMIN_*`, `SEED_EDITOR_*`.

Если `OPENCODE_API_KEY` не задан, AI-ассистент отвечает деградированным
сообщением (API недоступен) — остальной функционал работает.