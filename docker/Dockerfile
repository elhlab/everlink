FROM astral/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv export --locked --no-dev --no-emit-project --format requirements.txt \
    -o /tmp/requirements.txt

COPY src/ ./src/
RUN uv build

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /tmp/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir --no-deps /tmp/*.whl \
    && rm /tmp/*.whl

COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh

# The application listens on port 8000 by default.
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]