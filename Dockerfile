FROM ghcr.io/astral-sh/uv:alpine

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

WORKDIR /fastapi/

RUN apk add --no-cache ffmpeg

COPY ./.python-version ./
RUN uv python install

COPY ./pyproject.toml ./
RUN uv sync --upgrade

COPY ./src/ ./src/

CMD ["sh", "-c", "uv run fastapi run --app app --host 0.0.0.0 --port $FASTAPI_PORT --workers $(nproc) src/main.py"]
