FROM python:3.11-slim

# Install curl.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry.
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /bot/

WORKDIR /bot

RUN poetry install --no-root --only main

COPY ./bot /bot
COPY ./media /bot/media

# ???
COPY individual.db /bot

CMD [ "poetry", "run", "bot" ]
