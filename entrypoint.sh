#!/bin/sh

echo "Veritabanı göç işlemleri bekleniyor..."
# PostgreSQL'in hazır olmasını bekle
sleep 5

# Göç işlemlerini uygula
echo "Veritabanı göç işlemleri uygulanıyor..."
python manage.py migrate --noinput

# Statik dosyaları topla
echo "Statik dosyalar toplanıyor..."
python manage.py collectstatic --noinput

# Medya dizinlerinin varlığını kontrol et
echo "Medya dizinleri kontrol ediliyor..."
mkdir -p media/tour_images
mkdir -p media/tour_gallery
mkdir -p media/slider_images
chmod -R 755 media

# Görseller için izinleri ayarla
echo "Dosya izinleri ayarlanıyor..."
find . -type d -name "media" -exec chmod 755 {} \;
find . -type d -name "tour_images" -exec chmod 755 {} \;
find . -type d -name "tour_gallery" -exec chmod 755 {} \;

# uygulama çalıştır
echo "Uygulama başlatılıyor..."
exec gunicorn --bind 0.0.0.0:8000 mirzade.wsgi:application 