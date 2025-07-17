# ---------------------------
# Builder Stage
# ---------------------------
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# 安装依赖
RUN apt-get update && apt-get install -y \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==2.1.3

WORKDIR /app
COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.in-project true \
 && poetry install --no-root
RUN ls -lah /app && ls -lah /app/.venv

COPY . .

# ---------------------------
# Development Stage
# ---------------------------
FROM python:3.11-slim AS development

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 安装开发时需要的工具
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 拷贝虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 创建 logs 目录
RUN mkdir -p /app/logs

EXPOSE 8000

# 开发模式使用 reload
CMD ["uvicorn", "travel_buddy_ai.main:AppCreator.create_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------------------------
# Production Stage
# ---------------------------
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 只安装运行时需要的工具
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# 拷贝虚拟环境和项目文件
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/travel_buddy_ai /app/travel_buddy_ai
COPY --from=builder /app/.env.example /app/.env


# 创建 logs 目录并设置权限
RUN mkdir -p /app/logs && chown -R app:app /app

# 切换用户
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1


CMD ["uvicorn", "travel_buddy_ai.main:AppCreator.create_app", "--host", "0.0.0.0", "--port", "8000"]
