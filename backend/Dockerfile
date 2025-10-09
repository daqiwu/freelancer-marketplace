FROM python:3.12-slim

# Install necessary tools
RUN apt-get update && apt-get install -y curl git build-essential && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* /app/

# Install dependencies (no virtualenv, install to system environment)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy backend code
COPY . /app
