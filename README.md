# API для ЭСКРО

API сервис для сайта ЭСКРО, построенный на FastAPI с PostgreSQL.

### Локальный запуск

1. **Установите зависимости:**

   ```bash
   # Установка Poetry (если еще не установлен)
   pip install poetry

   # ИЛИ

   pip3 install poetry
   ```

2. **Настройте базу данных:**

   ```bash
   # Создайте базу данных PostgreSQL
   createdb eskro_db

   # Или используйте Docker для PostgreSQL
   docker run --name eskro-postgres -e POSTGRES_DB=eskro_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15-alpine
   ```

3. **Получите пароль приложения в своем почтовом клиенте**

   Документация для получения пароля приложения в Gmail:
   https://support.google.com/accounts/answer/185833?hl=ru

4. **Настройте переменные окружения:**

   По подобию `.env.example` создайте `.env` в папке `/app`. Пример файла:

   ```bash
   # Для минимальной настройки приложения необходимо поменять эти переменные в /app/.env:

   # Database
   DB__URL=postgresql+asyncpg://user:password@db:5432/eskro_db

   # Email
   EMAIL__USERNAME=admin@example.com
   EMAIL__PASSWORD=admin-password-app
   EMAIL__PORT=465
   EMAIL__SERVER=smtp.gmail.com

   # Admin
   ADMIN__EMAIL=admin@example.com
   ADMIN__USERNAME=admin
   ```

5. **Настройте сертификаты**

   Из `/app/security/README.md` скопируйте команды и запустите их в корне проекта

6. **Запустите миграции:**

   ```bash
   cd app
   alembic upgrade head
   ```

7. **Запустите приложение:**

   ```bash
   cd app
   python main.py
   ```

   Приложение будет доступно по адресу: http://localhost:8000

### Запуск через Docker Compose

1. **Убедитесь, что у вас есть .env файл в папке app/** с необходимыми настройками

2. **Создайте папку uploads в корне проекта**

3. **Запустите приложение:**

   ```bash
   docker-compose up --build
   ```

4. **Приложение будет доступно по адресу:**
   - API: http://localhost:8000
   - API документация: http://localhost:8000/docs

## 📁 Структура проекта

```
eskro_api/
├── app/                    # Основное приложение
│   ├── api/               # API эндпоинты
│   ├── core/              # Основная логика
│   ├── migrations/        # Миграции базы данных
│   ├── main.py           # Точка входа
│   └── .env              # Переменные окружения
├── certs/                 # SSL сертификаты
├── uploads/              # Загруженные файлы
├── docker-compose.yml    # Docker Compose конфигурация
├── Dockerfile           # Docker образ
└── pyproject.toml       # Зависимости Python
```

## 🛠 Разработка

### Установка зависимостей для разработки

```bash
poetry install --with dev
```

### Создание миграций

```bash
cd app
alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций

```bash
cd app
alembic upgrade head
```

## 🐳 Docker команды

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Пересборка
docker-compose up --build

# Очистка volumes (ОСТОРОЖНО: удалит данные БД)
docker-compose down -v
```

## 📚 API Документация

После запуска приложения документация доступна по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚨 Устранение неполадок

### Проблемы с подключением к БД

1. Убедитесь, что PostgreSQL запущен
2. Проверьте правильность `DATABASE_URL` в `.env`
3. Убедитесь, что база данных `eskro_db` существует

### Проблемы с Docker

1. Убедитесь, что Docker и Docker Compose установлены
2. Проверьте, что порты 8000 и 5432 свободны
3. Запустите `docker-compose logs` для просмотра ошибок

### Проблемы с миграциями

1. Убедитесь, что вы находитесь в папке `app/`
2. Проверьте подключение к БД
3. Запустите `alembic current` для проверки текущей версии
