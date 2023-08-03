FROM python:3.11.4-bullseye AS base

ENV POETRY_HOME=/opt/poetry
ARG POETRY_VERSION=1.5.1

RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}
RUN $POETRY_HOME/bin/poetry --version

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY genia genia
COPY README.md ./
COPY ./entrypoint.sh ./

RUN $POETRY_HOME/bin/poetry install --no-interaction --no-ansi

EXPOSE 5001

ENTRYPOINT ["./entrypoint.sh"]
CMD ["local"]