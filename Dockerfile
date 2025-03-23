FROM python:3.11-alpine

# Çalışma dizinini belirleme
WORKDIR /app

# Gerekli paketleri yükleme
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev libffi-dev

# Python gereksinimleri için virtualenv kullanma
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Gereksinimleri kopyalama ve yükleme
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint betiğini kopyala ve çalıştırılabilir yap
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Uygulama kodunu kopyalama
COPY . /app/

# Entrypoint betiğini çalıştır
ENTRYPOINT ["/app/entrypoint.sh"] 