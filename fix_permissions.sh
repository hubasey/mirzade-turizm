#!/bin/bash

# Renkli çıktı için
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}==>${NC} Media dizini izinleri düzeltiliyor..."

# Media ana dizini ve alt dizinleri
mkdir -p media/tour_images
mkdir -p media/tour_gallery
mkdir -p media/slider_images

# İzinleri düzeltme
chmod -R 755 media
find media -type d -exec chmod 755 {} \;
find media -type f -exec chmod 644 {} \;

# Docker ile çalışıyorsa, container içindeki izinleri düzeltme
if [ -x "$(command -v docker)" ]; then
    echo -e "${GREEN}==>${NC} Docker container içi izinler düzeltiliyor..."
    
    # Web container adını al
    WEB_CONTAINER=$(docker ps --filter "name=mirzade_web" --format "{{.Names}}")
    
    if [ -n "$WEB_CONTAINER" ]; then
        docker exec -it $WEB_CONTAINER sh -c "mkdir -p /app/media/tour_images && mkdir -p /app/media/tour_gallery && mkdir -p /app/media/slider_images && chmod -R 755 /app/media && find /app/media -type d -exec chmod 755 {} \; && find /app/media -type f -exec chmod 644 {} \;"
        echo -e "${GREEN}==>${NC} Container içi izinler düzeltildi."
    else
        echo -e "${GREEN}==>${NC} Docker çalışmıyor veya web container bulunamadı."
    fi
fi

echo -e "${GREEN}==>${NC} İşlem tamamlandı. Medya dosyaları izinleri düzeltildi." 