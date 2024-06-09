FROM python:3.12-slim as base

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt update && apt -y install build-essential git libpq5 ffmpeg libjpeg-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install poetry==1.8.2
RUN poetry config virtualenvs.create false

FROM base as prod

RUN poetry install --without dev,test --no-interaction --no-ansi

COPY ./app /app
COPY start.sh start.sh
RUN chmod +x /start.sh

WORKDIR /app
ENV PYTHONPATH=/app:/usr/lib/python3/dist-packages
EXPOSE 80
CMD ["/start.sh"]

FROM prod as dev

RUN poetry install --without test --no-interaction --no-ansi

FROM prod as test

RUN poetry install --without dev --no-interaction --no-ansi