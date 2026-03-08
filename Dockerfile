FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install uv

COPY . .

RUN chmod +x entrypoint.sh

RUN uv sync --frozen

CMD ["sh", "entrypoint.sh", "uv", "run", "python", "main.py"]
