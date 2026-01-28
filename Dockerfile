FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8080

# Run the application - Cloud Run sets PORT automatically
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
