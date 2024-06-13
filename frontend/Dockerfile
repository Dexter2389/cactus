FROM python:3.12-slim as base

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt update && apt -y install build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install poetry==1.8.2
RUN poetry config virtualenvs.create false

FROM base as prod

RUN poetry install --without dev,test --no-interaction --no-ansi

COPY ./app /app

WORKDIR /app
ENV PYTHONPATH=/app:/usr/lib/python3/dist-packages
EXPOSE 80
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=80"]

FROM prod as dev

RUN poetry install --without test --no-interaction --no-ansi

FROM prod as test

RUN poetry install --without dev --no-interaction --no-ansi