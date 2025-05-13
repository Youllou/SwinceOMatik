FROM python:3.11-slim

# Environment sanity
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ✅ Install cryptography build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 🔁 Copy requirement files
COPY discordClient/requirements.txt ./requirements-discord.txt
COPY swincer/requirements.txt ./requirements-swincer.txt
COPY pyproject.toml .

# ✅ Install pip deps
RUN pip install --upgrade pip
RUN pip install -r requirements-discord.txt
RUN pip install -r requirements-swincer.txt
RUN pip install -e . pymysql

# 📦 Copy all source code
COPY . ./SwinceOMatik

# Optional cleanup
RUN rm /app/SwinceOMatik/pyproject.toml

# 🚀 Launch the bot
CMD ["python", "SwinceOMatik/discordClient/__init__.py"]
