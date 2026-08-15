FROM python:3.14.5-alpine
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN ALPINE_VERSION=$(cat /etc/alpine-release | cut -d'.' -f1-2) && \
    echo "https://linux-mirror.liara.ir/repository/alpine/v${ALPINE_VERSION}/main" > /etc/apk/repositories && \
    echo "https://linux-mirror.liara.ir/repository/alpine/v${ALPINE_VERSION}/community" >> /etc/apk/repositories
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconf \
    libffi-dev \
    py3-uv
ENV UV_PROJECT_ENVIRONMENT=/venv
COPY pyproject.toml pyproject.toml
RUN uv sync
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]