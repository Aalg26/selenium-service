FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
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
    python3-tk \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome-stable_current_amd64.deb || true \
    && rm -f /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash appuser

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


RUN sbase install chromedriver || true
RUN chmod -R 777 /usr/local/lib/python3.11/site-packages/seleniumbase/drivers || true

COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5555

ENV PORT=5555
ENV HEADLESS=false
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

CMD ["sh", "-c", "xvfb-run -a --server-args='-screen 0 800x600x24' uvicorn main:app --host 0.0.0.0 --port $PORT --reload"]