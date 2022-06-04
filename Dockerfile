ARG PYTHON_VERSION=3.8.12

#####
# Set the base image parameters
#####
FROM python:${PYTHON_VERSION}-slim-buster

# System environment variables:
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  CRYPTOGRAPHY_DONT_BUILD_RUST=1 \
  # poetry:
  POETRY_VERSION=1.1.13 \
  PATH="$PATH:/root/.local/bin"

COPY install-packages.sh .
RUN chmod +x install-packages.sh && ./install-packages.sh

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | POETRY_VERSION="$POETRY_VERSION" python -

# Requirements are installed here to ensure they will be cached.
WORKDIR /tmp
COPY poetry.lock pyproject.toml /tmp/
RUN POETRY_VIRTUALENVS_CREATE=false poetry install $(if [ "$POETRY_ENV" = 'production' ]; then echo '--no-dev'; fi)

RUN mkdir -p /src
COPY src/ /src/
COPY tests/ /tests/

WORKDIR /src
CMD uvicorn main:app --proxy-headers --host 0.0.0.0 --port 8000
