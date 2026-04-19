FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install "fastapi[standard]" "uvicorn[standard]" websockets httpx pydantic python-dotenv

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
