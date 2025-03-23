#!/bin/bash

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
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

# Değişkenler
APP_DIR="/opt/mirzade"
GIT_REPO=${1:-"https://github.com/hubasey/mirzade-turizm.git"}
GIT_BRANCH=${2:-"master"}
BACKUP_DIR="${APP_DIR}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP="${BACKUP_DIR}/pre_deploy_${TIMESTAMP}_db.sql.gz"

# Yedekleme fonksiyonu
backup() {
    log "Veritabanı yedekleniyor..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p $BACKUP_DIR
    fi
    
    # Docker compose üzerinden veritabanı yedeği alma
    cd $APP_DIR
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > $DB_BACKUP
    
    if [ $? -ne 0 ]; then
        error "Veritabanı yedeği alınamadı."
        exit 1
    fi
    
    log "Veritabanı yedeği alındı: $DB_BACKUP"
}

# Kodu güncelleme
update_code() {
    log "Kod güncelleniyor..."
    
    # Dizin yoksa klonla
    if [ ! -d "${APP_DIR}/.git" ]; then
        log "Git repo klonlanıyor..."
        git clone -b $GIT_BRANCH $GIT_REPO $APP_DIR
    else
        # Var olan repoyu güncelle
        cd $APP_DIR
        git fetch
        git reset --hard origin/$GIT_BRANCH
    fi
    
    if [ $? -ne 0 ]; then
        error "Kod güncellenirken bir hata oluştu."
        exit 1
    fi
    
    log "Kod başarıyla güncellendi."
}

# Docker servislerini yeniden başlatma
restart_services() {
    log "Docker servisleri yeniden başlatılıyor..."
    
    cd $APP_DIR
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d --build
    
    if [ $? -ne 0 ]; then
        error "Docker servisleri yeniden başlatılırken bir hata oluştu."
        exit 1
    fi
    
    log "Docker servisleri başarıyla yeniden başlatıldı."
}

# İzinleri ayarla
fix_permissions() {
    log "Dosya izinleri ayarlanıyor..."
    
    cd $APP_DIR
    find . -type d -exec chmod 755 {} \;
    find . -type f -exec chmod 644 {} \;
    chmod +x scripts/*.sh
    chmod +x entrypoint.sh
    
    log "Dosya izinleri başarıyla ayarlandı."
}

# Ana işlev
main() {
    log "Mirzade Turizm dağıtım betiği başlatılıyor..."
    
    # Güncelleme öncesi yedekleme
    backup
    
    # Kodu güncelle
    update_code
    
    # İzinleri ayarla
    fix_permissions
    
    # Servisleri yeniden başlat
    restart_services
    
    log "Dağıtım işlemi başarıyla tamamlandı."
    log "Uygulamaya şu adresten erişebilirsiniz: https://mirzadeturizm.com"
}

# Ana işlevi çalıştır
main 