FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /eskro-api

RUN pip install --upgrade pip wheel "poetry==2.1.3"
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction

COPY app/ ./app/
COPY certs/ ./certs/
COPY uploads/ ./uploads/


CMD ["sh", "-c", "cd app && alembic upgrade head && exec python main.py"]