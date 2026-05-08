# Ecom Project

FastAPI-сервис для загрузки CSV с оценками студентов в PostgreSQL и получения простой аналитики по оценкам `2`.

## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- asyncpg
- Alembic
- pytest
- Docker Compose

## Быстрый запуск через Docker Compose

Из корня проекта:

```bash
docker compose up --build
```

Compose поднимает:

- `db` - PostgreSQL на порту `5432`;
- `backend` - FastAPI на порту `8000`.

Backend ждет готовности PostgreSQL, выполняет миграции:

```bash
alembic upgrade head
```

и затем запускает приложение:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

После запуска:

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

Остановить контейнеры:

```bash
docker compose down
```

Остановить и удалить volume с данными PostgreSQL:

```bash
docker compose down -v
```

## Локальный запуск без Docker

Команды ниже выполняются из папки `backend`.

Создать и активировать виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Создать `.env` в корне проекта или экспортировать переменные окружения:

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ecom
```

Применить миграции:

```bash
alembic upgrade head
```

Запустить backend:

```bash
uvicorn app.main:app --reload
```

## API

### POST `/upload-grades`

Загружает CSV-файл с оценками студентов.

Ожидаемые заголовки CSV:

```csv
ID,Name,Surname,Patronymic,Subject,Grade
```

Поддерживаются разделители `,`, `;` и tab.

Пример:

```csv
ID,Name,Surname,Patronymic,Subject,Grade
1,Ivan,Ivanov,Ivanovich,MATH,5
1,Ivan,Ivanov,Ivanovich,HISTORY,2
2,Petr,Petrov,,PHYSICS,2
```

Загрузка частичная: валидные строки сохраняются, ошибки возвращаются в поле `errors`.

Пример ответа:

```json
{
  "status": "ok",
  "records_loaded": 3,
  "students": 2,
  "errors": []
}
```

Если один `ID` встречается у студентов с разными ФИО, конфликтная строка пропускается и попадает в `errors`.

### GET `/students/more-than-3-twos`

Возвращает студентов, у которых оценка `2` встречается больше 3 раз.

```json
[
  {
    "full_name": "Ivanov Ivan Ivanovich",
    "count_twos": 5
  }
]
```

### GET `/students/less-than-5-twos`

Возвращает студентов, у которых оценка `2` встречается меньше 5 раз.

```json
[
  {
    "full_name": "Petrov Petr",
    "count_twos": 2
  }
]
```

## Тесты

Из папки `backend`:

```bash
python -m pytest tests
```

## Миграции

Миграции лежат в `backend/migrations`.

Применить миграции:

```bash
alembic upgrade head
```

Откатить последнюю миграцию:

```bash
alembic downgrade -1
```
