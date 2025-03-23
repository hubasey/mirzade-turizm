#!/bin/bash

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log fonksiyonları
log() {
    echo -e "[$(date +"%Y-%m-%d %H:%M:%S")] ${GREEN}$1${NC}"
}

error() {
    echo -e "[$(date +"%Y-%m-%d %H:%M:%S")] ${RED}HATA: $1${NC}" >&2
}

warning() {
    echo -e "[$(date +"%Y-%m-%d %H:%M:%S")] ${YELLOW}UYARI: $1${NC}"
}

# Root kullanıcı kontrolü
if [[ $EUID -ne 0 ]]; then
   error "Bu betik root yetkileri gerektirir. 'sudo ./setup.sh' komutu ile çalıştırın."
   exit 1
fi

# Sistem güncelleme
system_update() {
    log "Sistem güncelleniyor..."
    apt update && apt upgrade -y
    
    if [ $? -ne 0 ]; then
        error "Sistem güncellemesi sırasında bir hata oluştu."
        exit 1
    fi
    
    log "Sistem başarıyla güncellendi."
}

# Gerekli paketleri kurma
install_dependencies() {
    log "Gerekli paketler kuruluyor..."
    apt install -y curl git software-properties-common apt-transport-https ca-certificates gnupg lsb-release ufw fail2ban
    
    if [ $? -ne 0 ]; then
        error "Gerekli paketlerin kurulumu sırasında bir hata oluştu."
        exit 1
    fi
    
    log "Gerekli paketler başarıyla kuruldu."
}

# Docker kurulumu
install_docker() {
    log "Docker kuruluyor..."
    
    # Docker GPG anahtarını ekle
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Docker repo ekle
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Docker kur
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io
    
    if [ $? -ne 0 ]; then
        error "Docker kurulumu sırasında bir hata oluştu."
        exit 1
    fi
    
    # Docker'ı başlat ve sistem açılışında otomatik başlatılmasını sağla
    systemctl start docker
    systemctl enable docker
    
    log "Docker başarıyla kuruldu."
}

# Docker Compose kurulumu
install_docker_compose() {
    log "Docker Compose kuruluyor..."
    
    # Docker Compose'un son sürümünü indir
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Çalıştırma izni ver
    chmod +x /usr/local/bin/docker-compose
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose kurulumu sırasında bir hata oluştu."
        exit 1
    fi
    
    log "Docker Compose başarıyla kuruldu. Sürüm: ${COMPOSE_VERSION}"
}

# Firewall yapılandırması
configure_firewall() {
    log "Firewall yapılandırılıyor..."
    
    # Varsayılanı reddet
    ufw default deny incoming
    ufw default allow outgoing
    
    # SSH, HTTP ve HTTPS izin ver
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Firewall'u etkinleştir
    echo "y" | ufw enable
    
    log "Firewall başarıyla yapılandırıldı."
}

# Fail2ban yapılandırması
configure_fail2ban() {
    log "Fail2ban yapılandırılıyor..."
    
    # Fail2ban servisini başlat
    systemctl start fail2ban
    systemctl enable fail2ban
    
    # Konfigürasyon dosyasını oluştur
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
EOF

    # Servisi yeniden başlat
    systemctl restart fail2ban
    
    log "Fail2ban başarıyla yapılandırıldı."
}

# Dizin yapısını oluştur
create_directory_structure() {
    log "Dizin yapısı oluşturuluyor..."
    
    # Dizinleri oluştur
    mkdir -p /opt/mirzade/logs
    mkdir -p /opt/mirzade/backups
    mkdir -p /opt/mirzade/nginx/conf.d
    mkdir -p /opt/mirzade/nginx/certbot/conf
    mkdir -p /opt/mirzade/nginx/certbot/www
    
    # İzinleri ayarla
    chmod -R 755 /opt/mirzade
    
    log "Dizin yapısı başarıyla oluşturuldu."
}

# Env dosyası kontrolü
check_env_file() {
    log "Çevresel değişkenler kontrol ediliyor..."
    
    if [ ! -f "/opt/mirzade/.env.prod" ]; then
        warning "'.env.prod' dosyası bulunamadı. Örnek dosya kopyalanıyor..."
        cp /opt/mirzade/.env.prod.example /opt/mirzade/.env.prod
        warning "Lütfen '.env.prod' dosyasını düzenleyerek gerekli değişkenleri ayarlayın."
    else
        log "'.env.prod' dosyası mevcut."
    fi
}

# Ana işlev
main() {
    log "Mirzade Turizm sunucu kurulum betiği başlatılıyor..."
    
    system_update
    install_dependencies
    install_docker
    install_docker_compose
    configure_firewall
    configure_fail2ban
    create_directory_structure
    check_env_file
    
    log "Kurulum tamamlandı!"
    log "Sonraki adımlar:"
    echo -e "${BLUE}1. .env.prod dosyasını düzenleyin:${NC} nano /opt/mirzade/.env.prod"
    echo -e "${BLUE}2. Docker servislerini başlatın:${NC} cd /opt/mirzade && docker-compose -f docker-compose.prod.yml up -d"
    echo -e "${BLUE}3. SSL sertifikası alın:${NC} docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d mirzadeturizm.com -d www.mirzadeturizm.com --email admin@mirzadeturizm.com --agree-tos --no-eff-email"
    echo -e "${BLUE}4. Tüm servisleri yeniden başlatın:${NC} docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"
    
    log "Mirzade Turizm sunucu kurulumu başarıyla tamamlandı."
}

# Ana işlevi çalıştır
main 