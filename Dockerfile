# ── Stage 1: base image ───────────────────────────────────────────────────────
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (cached layer — only re-runs when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and templates
COPY src/       ./src/
COPY templates/ ./templates/

# Move into the src directory so calculator.py is importable by app.py
WORKDIR /app/src

# Expose the port uvicorn will listen on
EXPOSE 5000

# Start the FastAPI app via uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
