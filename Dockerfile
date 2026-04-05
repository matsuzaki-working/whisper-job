# 必須パッケージ
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 依存関係を先にコピー（キャッシュ効く）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY . .

# Cloud Run JobではPORT不要（あってもOK）
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
