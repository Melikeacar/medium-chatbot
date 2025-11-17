# 1) Küçük boyutlu Python imajı
FROM python:3.11-slim

# 2) Sağlık kontrolü için curl kur
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
 rm -rf /var/lib/apt/lists/*

# 3) Çalışma dizinini ayarla - BU ÇOK ÖNEMLİ
WORKDIR /app

# 4) Gereksiz rebuild önlemek için requirements.txt’yi önce kopyala
COPY requirements.txt /app/

# 5) Bağımlılıkları yükle
RUN pip install --no-cache-dir -r requirements.txt

# 6) Proje dosyalarını kopyala
COPY . /app

# 7) Güvenlik: non-root kullanıcı
RUN useradd -m appuser
USER appuser

# 8) Flask portunu aç
EXPOSE 5000

# 9) Healthcheck (senin /health endpoint’in var)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
 CMD curl -f http://localhost:5000/health || exit 1

# 10) Uygulamayı Gunicorn ile başlat
# src/main.py içindeki "app" nesnesini kullanıyoruz
CMD ["gunicorn", "src.main:app", "-b", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120"]