FROM python:3.12-slim

# 安装必要工具
RUN apt-get update && apt-get install -y curl git build-essential && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 添加 Poetry 到 PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# 复制 pyproject.toml 和 poetry.lock
COPY pyproject.toml poetry.lock* /app/

# 安装依赖（无虚拟环境，直接安装到系统环境）
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 复制后端代码
COPY . /app
