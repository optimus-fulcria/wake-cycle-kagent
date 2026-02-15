FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create data directory
RUN mkdir -p /data

# Run as non-root user
RUN useradd -m -u 1000 agent
USER agent

# Environment defaults
ENV STATE_PATH=/data/state.json
ENV BACKLOG_PATH=/data/backlog.json
ENV ACCOMPLISHMENTS_PATH=/data/accomplishments.json
ENV LOG_LEVEL=info
ENV PORT=8000

EXPOSE 8000

CMD ["python", "main.py"]
