FROM python:3.12-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install lightweight requirements (no pgvector/psycopg2/sqlalchemy)
COPY requirements.render.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/


# Set working directory to backend
WORKDIR /app/backend

# Disable pre-warming to save startup memory
ENV DISABLE_PREWARM=1

# Expose port
EXPOSE 8000

# Start with $PORT environment variable assigned by Render cloud platform
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
