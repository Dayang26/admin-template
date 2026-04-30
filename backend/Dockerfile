FROM python:3.12-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy the project requirements
COPY pyproject.toml ./
COPY uv.lock* ./

# Install the dependencies using uv
# Falls back to non-frozen if uv.lock is missing
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy the rest of the application code
COPY . .

EXPOSE 8000

# Start the FastAPI application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
