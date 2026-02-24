FROM python:3.11-slim

# Añadimos xvfb a tu lista de paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    xvfb \
    xauth \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libx11-6 \
    libxext6 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome-stable_current_amd64.deb || true \
    && rm -f /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5555

ENV PORT=5555
ENV HEADLESS=true

# EL CAMBIO MÁS IMPORTANTE: Usamos xvfb-run para simular el monitor 
# al levantar tu API de FastAPI/Uvicorn
CMD ["sh", "-c", "xvfb-run -a uvicorn main:app --host 0.0.0.0 --port $PORT"]