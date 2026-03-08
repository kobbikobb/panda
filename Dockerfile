FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install uv

COPY . .

RUN chmod +x entrypoint.sh

RUN uv sync --frozen

CMD ["sh", "entrypoint.sh", "uv", "run", "python", "main.py"]
