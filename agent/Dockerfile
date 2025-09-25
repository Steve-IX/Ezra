FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash ezra
USER ezra

# Expose port (if needed)
EXPOSE 8080

# Start the agent
CMD ["python", "-m", "ezra_agent.main", "start", "--daemon"]
