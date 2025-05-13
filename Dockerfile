# Use slim Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (for psycopg2 / sqlite / etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*



COPY pyproject.toml ./pyproject.toml
COPY discordClient/requirements.txt ./SwinceOMatik/discordClient/requirements.txt
COPY discordClient/requirements.txt ./requirements.txt


RUN python -m venv venv
RUN . venv/bin/activate

# Install Python dependencies (merge them here)
RUN pip install --upgrade pip
RUN pip install -e . pymysql

COPY . ./SwinceOMatik
RUN rm /app/SwinceOMatik/pyproject.toml

# Command to run your bot
CMD ["python", "SwinceOMatik/discordClient/__init__.py"]
