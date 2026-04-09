# Тестовое задание Fullstack Developer

MVP файлообменника с backend на FastAPI и frontend на Next.js/React.

Приложение умеет:

- загружать файлы;
- сохранять их метаданные;
- проверять файл на подозрительные признаки;
- извлекать базовые метаданные;
- создавать алерты по результатам обработки;
- показывать файлы и алерты в UI;
- пагинировать списки `GET /files` и `GET /alerts`.

## Что сделано

### Backend

- Проведен рефакторинг из плоской структуры в слои:
  - `src/core` — конфигурация;
  - `src/db.py` — инициализация БД и session factory;
  - `src/repositories` — доступ к данным;
  - `src/services` — бизнес-логика;
  - `src/api/routes` — HTTP-слой;
  - `src/tasks.py` — очередь фоновой обработки.
- Добавлена общая схема пагинации.
- Исправлено удаление файла, у которого уже есть связанные алерты.
- Исправлены настройки `docker-compose` для Postgres volume и host-port.
- Миграция обновлена на каскадное удаление `alerts -> files`.
- Убран import-blocker FastAPI-приложения в урезанном локальном окружении:
  эндпоинт загрузки теперь парсит multipart через `Request.form()`, поэтому импорт `src.app`
  не падает при отсутствии `python-multipart` до фактического вызова upload-ручки.
- Добавлен fallback для задач без установленного `celery`, чтобы код можно было импортировать и тестировать локально.
- Docker-сборка backend приведена к рабочему состоянию.

### Frontend

- Логика разбита по слоям:
  - `src/shared` — API, типы, форматирование;
  - `src/features/dashboard/components` — UI-компоненты;
  - `src/features/dashboard/hooks` — управление данными экрана;
  - `src/app/page.tsx` — композиция страницы.
- Добавлена пагинация для таблиц файлов и алертов.
- Исправлены метаданные layout и путь к favicon.
- Добавлен `tsconfig` alias `@/*`.
- Добавлен скрипт `npm run typecheck`.
- Docker-сборка frontend приведена к рабочему состоянию.

## Архитектурное решение

### Backend

Основная идея — отделить инфраструктуру от бизнес-логики:

- роуты знают только про HTTP и dependency injection;
- сервисы знают сценарии приложения;
- репозитории знают SQLAlchemy и работу с БД;
- конфигурация централизована в `Settings`.

Такой разрез уменьшает связность, упрощает тестирование и делает код расширяемым:
например, пагинация или смена способа хранения не размазываются по всему проекту.

### Frontend

Основная идея — убрать “толстую страницу”, где были смешаны:

- запросы к API;
- UI-таблицы;
- форматирование дат и размеров;
- пагинация;
- управление модалкой и загрузкой.

Теперь страница выступает контейнером, а детали вынесены в `shared`, `features` и `components`.

## Структура проекта

```text
backend/
  migrations/
  src/
    api/
    core/
    repositories/
    services/
    app.py
    db.py
    models.py
    schemas.py
    tasks.py
  tests/

frontend/
  src/
    app/
    features/
    shared/
```

## API

### `GET /files`

Параметры:

- `page` — номер страницы, по умолчанию `1`;
- `per_page` — размер страницы, по умолчанию `10`, максимум `100`.

Ответ:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "per_page": 10,
  "total_pages": 0
}
```

### `GET /alerts`

Поддерживает те же параметры и тот же формат ответа, что и `GET /files`.

## Запуск

### Вариант 1. Через Docker Compose

1. Поднять сервисы:

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

2. Применить миграции:

```bash
docker exec -it backend alembic upgrade head
```

3. Открыть:

- frontend: [http://localhost:3000/test](http://localhost:3000/test)
- backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Вариант 2. Локальный запуск backend

Требования:

- Python 3.12+;
- PostgreSQL;
- Redis;
- зависимости из `backend/pyproject.toml`.

Пример:

```bash
cd backend
uv sync
alembic upgrade head
uvicorn src.app:app --reload --port 8000
```

Примечание:

- для реальной загрузки файлов на endpoint `POST /files` должен быть установлен `python-multipart`;
- без него приложение всё равно импортируется, но upload endpoint вернет ошибку только в момент вызова.

### Вариант 3. Локальный запуск frontend

Требования:

- Node.js 20.9+;
- npm.

Пример:

```bash
cd frontend
npm ci
npm run typecheck
npm run build
npm run dev
```

## Проверка

### Проверено локально

- `cd backend && pytest`
- `cd backend && python -m compileall src`
- `cd backend && python -c "from src.app import app; print(len(app.routes))"`
- `cd frontend && npm ci`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`

### Проверено в Docker

- `docker build -t test-project-frontend-check ./frontend`
- `docker build -t test-project-backend-check ./backend`
- `docker compose -f docker-compose.dev.yml up --build -d`
- `docker exec backend alembic upgrade head`

### Текущее состояние compose-стека

После проверки поднимаются сервисы:

- `frontend` на `http://localhost:3000`
- `backend` на `http://localhost:8000`
- `backend-db` на `localhost:5433`
- `backend-redis`
- `backend-worker`

Приложение доступно по заданным адресам:

- frontend: [http://localhost:3000/test](http://localhost:3000/test)
- backend docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Тесты

Добавлены backend-тесты на ключевые сценарии:

- расчет пагинации;
- отклонение пустого файла;
- определение suspicious-файла;
- извлечение текстовых метаданных;
- удаление файла вместе со связанными алертами.

Файлы тестов:

- `backend/tests/test_services.py`

## Основные исправления багов

- удаление файла больше не падает при наличии связанных алертов;
- списки файлов и алертов не выгружаются целиком без ограничений;
- frontend больше не держит весь экран, запросы и состояние в одном файле;
- исправлены ошибочные настройки Postgres в `docker-compose.dev.yml`;
- исправлен общий DX для локального импорта backend-приложения;
- исправлены Dockerfile-ы frontend и backend для реальной production-сборки;
- исправлена конфигурация Postgres volume для совместимости с актуальным образом `postgres:latest`.

## Дополнительно

- Next.js автоматически дополнил `frontend/tsconfig.json` настройками, ожидаемыми для проекта на App Router:
  `jsx: "react-jsx"`, plugin `next` и `.next/...` в `include`. Эти изменения сохранены.

## Возможные дальнейшие улучшения

- добавить интеграционные API-тесты на SQLite/Postgres test DB;
- добавить фронтенд-тесты для пагинации и загрузки;
- вынести константы статусов и уровней в enum;
- добавить линтеры и CI;
- добавить polling или optimistic refresh после загрузки файла;
- расширить метаданные файлов и правила сканирования.
