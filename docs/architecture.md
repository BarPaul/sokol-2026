# Architecture

## 1. Общая архитектура

Docker не используется.

Приложение запускается непосредственно на сервере/локальной машине.

```text
                    Browser
                       |
                       v
                   NuxtJS 4
                (Vue 3 / Nuxt UI)
                       |
                 REST API (HTTP)
                       |
                       v
                 FastAPI (Python)
                       |
           +------------+-------------+
           |            |             |
           v            v             v
       SQLite3      AI Service    Auth/RBAC
           |            |
           |            v
           |      OpenCode API
           |            |
           |            v
           |    Deepseek-v4-flash
           |
           v
   FTS5 Knowledge Base
```

Frontend — Nuxt 4 (Vue 3, TypeScript, Nuxt UI/Tailwind).

Backend — отдельный сервис на FastAPI (Python), который предоставляет REST API.

Frontend никогда не обращается к базе данных напрямую.

## 2. Стек

### Frontend

* NuxtJS 4;
* Vue 3;
* TypeScript;
* Nuxt UI / Tailwind CSS;
* VueUse;
* Zod.

### Backend

* FastAPI;
* Pydantic;
* SQLAlchemy;
* Alembic;
* JWT authentication.

### Database

* SQLite3;
* SQLite FTS5.

### ORM / Database layer

* SQLAlchemy (backend).

Схема:

```text
FastAPI
    ↓
SQLAlchemy
    ↓
SQLite3
```

### AI

* OpenCode API;
* модель `Deepseek-v4-flash`;
* OpenAI-compatible HTTP client;
* отдельный `AIService`.

## 3. Структура проекта

```text
semyainfo/
├── frontend/                 # Nuxt 4 (Vue 3, TS, Nuxt UI)
│   ├── app.vue
│   ├── components/
│   │   ├── common/
│   │   ├── article/
│   │   ├── assistant/
│   │   ├── editor/
│   │   └── admin/
│   │
│   ├── composables/
│   │
│   ├── layouts/
│   │   ├── default.vue
│   │   ├── editor.vue
│   │   └── admin.vue
│   │
│   ├── middleware/
│   │   ├── auth.ts
│   │   ├── editor.ts
│   │   └── admin.ts
│   │
│   ├── pages/
│   │   ├── index.vue
│   │   ├── articles/
│   │   ├── search.vue
│   │   ├── assistant.vue
│   │   ├── login.vue
│   │   ├── password-recovery.vue
│   │   ├── editor/
│   │   └── admin/
│   │
│   ├── shared/
│   │   ├── types/
│   │   └── schemas/
│   │
│   ├── public/
│   │
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   ├── package.json
│   └── .env
│
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── articles.py
│   │   │   ├── assistant.py
│   │   │   ├── editor.py
│   │   │   ├── admin.py
│   │   │   └── knowledge.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   │
│   │   ├── models/
│   │   │   └── sqlalchemy models
│   │   │
│   │   ├── schemas/
│   │   │   └── pydantic schemas
│   │   │
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   ├── articles/
│   │   │   ├── auth/
│   │   │   ├── knowledge/
│   │   │   └── audit/
│   │   │
│   │   └── db/
│   │       ├── base.py
│   │       └── session.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── tests/
│   │
│   ├── alembic.ini
│   ├── .env.example
│   ├── requirements.txt
│   └── main.py
│
├── data/
│   └── semyainfo.sqlite
│
├── docs/
│   ├── functional-spec.md
│   ├── architecture.md
│   ├── design-reference.md
│   └── design/
│
├── .env.example
├── .gitignore
└── README.md
```

## 4. SQLite

Основной файл:

```text
data/semyainfo.sqlite
```

Не хранить SQLite-файл в Git.

В `.gitignore`:

```text
/data
*.sqlite
*.sqlite3
*.db
```

## 5. Database schema

### accounts

```text
id
first_name
last_name
email
password_hash
role_id
status
created_at
updated_at
last_login_at
```

### roles

```text
id
name
```

### articles

```text
id
title
slug
summary
content
category
region
official_source
restrictions
status
author_id
created_at
updated_at
published_at
```

### article_authors

```text
article_id
account_id
```

### chats

```text
id
session_id
title
created_at
updated_at
```

### messages

```text
id
chat_id
role
content
created_at
```

### knowledge_documents

```text
id
title
content
source
category
is_active
created_at
updated_at
```

### ai_settings

```text
id
system_prompt
model
temperature
max_tokens
knowledge_enabled
updated_at
```

### logs

```text
id
account_id
action
entity_type
entity_id
result
description
metadata
created_at
```

## 6. FTS5

Создать отдельную SQLite FTS5 virtual table:

```text
knowledge_search
```

Индексировать:

```text
title
content
category
```

Синхронизация:

```text
Article published
       ↓
knowledge_documents
       ↓
FTS5 index
```

При изменении статьи индекс должен обновляться.

## 7. AI Service

Создать:

```text
backend/app/services/ai/
```

Интерфейс:

```python
from typing import Protocol

class AIProvider(Protocol):
    def generate(self, messages, options=None) -> dict:
        ...
```

Реализация:

```text
OpenCodeProvider
```

Конфигурация:

```env
OPENCODE_API_KEY=
OPENCODE_BASE_URL=
OPENCODE_MODEL=Deepseek-v4-flash
```

Точное значение `OPENCODE_BASE_URL` должно соответствовать endpoint, предоставленному используемым аккаунтом/агрегатором OpenCode. Не хардкодить URL в исходном коде.

## 8. AI request pipeline

```text
POST /api/assistant/chats/:id/messages
              |
              v
         AssistantService
              |
              +---- load AI settings
              |
              +---- search knowledge
              |
              +---- build context
              |
              +---- build messages
              |
              v
         OpenCodeProvider
              |
              v
       Deepseek-v4-flash
              |
              v
           AI response
              |
        +-----+------+
        |            |
        v            v
     Message      Articles
        |            |
        +-----+------+
              |
              v
           frontend
```

## 9. System prompt

System prompt хранится в:

```text
ai_settings.system_prompt
```

При каждом запросе:

```text
system prompt
      +
knowledge context
      +
chat history
      +
current user message
```

Не хранить системный prompt в frontend.

Не разрешать анонимному пользователю изменять system prompt.

Изменять его может только администратор.

## 10. Knowledge Base

Основной источник:

```text
published articles
```

Дополнительный источник:

```text
knowledge_documents
```

Поиск:

```text
question
  ↓
FTS5
  ↓
top K documents
  ↓
context
```

Рекомендуемый `K` для MVP: 5.

Это значение вынести в конфигурацию.

## 11. API

### Auth

```http
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
POST /api/auth/password-recovery
```

### Public articles

```http
GET /api/articles
GET /api/articles/:slug
GET /api/articles/search
GET /api/articles/categories
```

### Assistant

```http
POST /api/assistant/chats
GET  /api/assistant/chats
GET  /api/assistant/chats/:id
DELETE /api/assistant/chats/:id

GET  /api/assistant/chats/:id/messages
POST /api/assistant/chats/:id/messages
```

### Editor

```http
GET    /api/editor/articles
POST   /api/editor/articles
GET    /api/editor/articles/:id
PATCH  /api/editor/articles/:id
DELETE /api/editor/articles/:id
POST   /api/editor/articles/:id/publish

POST   /api/editor/articles/:id/coauthors
DELETE /api/editor/articles/:id/coauthors/:accountId
```

### Admin

```http
GET   /api/admin/editors
POST  /api/admin/editors
GET   /api/admin/editors/:id
PATCH /api/admin/editors/:id

GET /api/admin/logs
GET /api/admin/logs/:id
```

### AI settings

```http
GET   /api/admin/ai/settings
PATCH /api/admin/ai/settings
```

### Knowledge

```http
GET    /api/admin/knowledge
POST   /api/admin/knowledge
GET    /api/admin/knowledge/:id
PATCH  /api/admin/knowledge/:id
DELETE /api/admin/knowledge/:id
POST   /api/admin/knowledge/reindex
```

## 12. Authentication

Backend на FastAPI использует **JWT**.

Токен передаётся через `Authorization: Bearer <token>`.

Для MVP:

* access token с ограниченным временем жизни;
* секрет в `JWT_SECRET` (environment variable).

Nuxt frontend хранит токен на клиенте (cookie/localStorage) и передаёт в заголовке.

Секреты не хранить в `NUXT_PUBLIC_*`.

Каждый защищённый endpoint проверяет JWT и роль на backend.

## 13. Authorization

Frontend middleware:

```text
auth
editor
admin
```

Но middleware frontend не является защитой.

Каждый server endpoint FastAPI дополнительно проверяет роль (dependency / permission).

```text
anonymous
    ↓
public endpoints

editor
    ↓
editor endpoints

moderator
    ↓
admin endpoints
```

## 14. Audit

Все административные операции проходят через:

```text
AuditService
```

Пример:

```text
ArticleService
      ↓
database mutation
      ↓
AuditService.log()
```

## 15. Runtime

Запуск без Docker:

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Production:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

cd frontend
npm run build
```

## 16. Environment

```env
# backend
DATABASE_URL=sqlite:///./data/semyainfo.sqlite
JWT_SECRET=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=1440

OPENCODE_API_KEY=
OPENCODE_BASE_URL=
OPENCODE_MODEL=Deepseek-v4-flash

# frontend
NUXT_PUBLIC_API_BASE=http://localhost:8000
NUXT_PUBLIC_APP_NAME=СтудСемья
```

Секреты:

* не помещать в `NUXT_PUBLIC_*`;
* не хранить в Git;
* не отдавать клиенту.

## 17. Архитектурные ограничения

Не использовать:

* Docker;
* PostgreSQL;
* прямой вызов OpenCode из браузера;
* API key во frontend;
* mock AI вместо реального API;
* frontend-only authorization.

Главная бизнес-логика находится в `backend/app/services`.

Vue-компоненты не должны содержать SQL или логику обращения к OpenCode API.