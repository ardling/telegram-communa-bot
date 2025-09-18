FROM python:3.12-slim AS reqs
WORKDIR /app
RUN pip install poetry poetry-plugin-export
COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt


FROM python:3.12-slim AS build
WORKDIR /app
RUN pip install poetry
COPY . .
RUN poetry build


FROM python:3.12-slim

RUN useradd -m botuser
COPY --from=reqs /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=build /app/dist/telegram_communa_bot-*.whl .
RUN pip install telegram_communa_bot-*.whl

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1

USER botuser

CMD ["telegram-communa-bot"]
