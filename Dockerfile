# Base estable de Ubuntu
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV UV_PYTHON=3.12.3
# FORZAMOS a que uv cree el entorno FUERA de /app para que el volumen no lo tape
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update && apt-get install -y \
    curl ca-certificates iverilog make gcc g++ git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Instalamos Python y dependencias en /opt/venv (zona segura)
WORKDIR /setup
COPY pyproject.toml uv.lock ./
RUN uv python install $UV_PYTHON
RUN uv sync --frozen --python $UV_PYTHON

# Agregamos el entorno virtual al PATH para que 'make' vea 'cocotb-config'
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
# No copiamos todo aquí para que el build sea rápido, 
# el código entrará por el volumen -v o por el COPY final
COPY . .

CMD ["make"]