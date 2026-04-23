FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /uvx /bin/
COPY . /app

ENV UV_NO_DEV=1

WORKDIR /app
RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["uv", "run" , "main.py"] 