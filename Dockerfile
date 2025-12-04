# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install the project package in editable mode
RUN pip install -e .

# Expose ports for Streamlit and FastAPI
EXPOSE 8501 8000

# Default to running Streamlit; can override with command
CMD ["streamlit", "run", "mediapulse/ui_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
