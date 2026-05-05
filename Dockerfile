# ─── Python 3.10 Slim Tabanlı Docker Image ───────────────────
FROM python:3.10-slim

# Çalışma dizinini oluştur
WORKDIR /app

# Önce requirements.txt'i kopyala (cache optimizasyonu)
COPY app/requirements.txt .

# Bağımlılıkları kur
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY app/ .

# Render, PORT env variable'ını otomatik atar
# Gunicorn bu değişkeni kullanarak doğru portta dinleyecek
EXPOSE 5000

# Gunicorn ile uygulamayı başlat
# Render $PORT değişkenini sağlar; yoksa 5000 kullanılır
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app
