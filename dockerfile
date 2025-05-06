FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["python", "main.py"]
