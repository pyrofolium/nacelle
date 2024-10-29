FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Set environment variables to prevent Python from buffering stdout and to install Poetry globally
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.6.1 \
    PATH="$PATH:/root/.local/bin"

# Install Poetry, pip, and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Gunicorn and Uvicorn through Poetry
RUN pip install --upgrade pip

# Copy the entire project
COPY . .

# Install dependencies (runtime only)
RUN poetry install --no-dev

#bootstrap
RUN python bootstrap.py


# Expose the port that the application will run on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "server:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]