#!/bin/bash

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# İşlevi tanımla
print_message() {
    echo -e "${GREEN}==>${NC} $1"
}

# Hata işlevi tanımla
print_error() {
    echo -e "${RED}==>${NC} $1"
}

# Uyarı işlevi tanımla
print_warning() {
    echo -e "${YELLOW}==>${NC} $1"
}

# Kontrolleri yap
if [ ! -f ".env" ]; then
    print_error ".env dosyası bulunamadı!"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml dosyası bulunamadı!"
    exit 1
fi

# Docker ve Docker Compose yükleme
print_message "Docker ve Docker Compose yükleniyor..."
apt-get update
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-compose

# Docker servisini başlat
print_message "Docker servisini başlatma..."
systemctl start docker
systemctl enable docker

# Gerekli dizinleri oluştur
print_message "Gerekli dizinleri oluşturma..."
mkdir -p config/certbot/conf
mkdir -p config/certbot/www
mkdir -p media/tour_images
mkdir -p media/tour_gallery

# İzinleri ayarla
print_message "Dosya izinlerini ayarlama..."
chmod -R 755 media
chmod +x entrypoint.sh

# Docker Compose ile servisleri başlat
print_message "Docker Compose ile servisleri başlatma..."
docker-compose -f docker-compose.yml up -d

print_message "Kurulum tamamlandı!"
print_message "Web uygulaması: http://localhost"
print_warning "Unutmayın, HTTPS yapılandırması için Let's Encrypt sertifikası almanız gerekecek." 