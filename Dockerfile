FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
RUN pip install uv

COPY . .

RUN uv sync --frozen

CMD ["uv", "run", "python", "main.py"]
