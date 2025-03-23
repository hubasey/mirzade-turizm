#!/bin/bash

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Log fonksiyonu
log() {
    echo -e "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

# Kullanım bilgisi
show_usage() {
    echo "Kullanım: ./restore.sh <db_backup> <media_backup>"
    echo "Örnek: ./restore.sh /backups/mirzade_backup_20250101_120000_db.sql.gz /backups/mirzade_backup_20250101_120000_media.tar.gz"
    echo ""
    echo "Mevcut yedeklemeler:"
    find /backups -name "mirzade_backup_*" -type f | sort
}

# Ana geri yükleme işlevi
main() {
    if [ "$#" -ne 2 ]; then
        log "${RED}HATA: Eksik parametreler.${NC}"
        show_usage
        exit 1
    fi
    
    DB_BACKUP=$1
    MEDIA_BACKUP=$2
    
    # Yedekleme dosyalarını kontrol et
    if [ ! -f "$DB_BACKUP" ]; then
        log "${RED}HATA: Veritabanı yedekleme dosyası ($DB_BACKUP) bulunamadı.${NC}"
        exit 1
    fi
    
    if [ ! -f "$MEDIA_BACKUP" ]; then
        log "${RED}HATA: Medya yedekleme dosyası ($MEDIA_BACKUP) bulunamadı.${NC}"
        exit 1
    fi
    
    # Kullanıcıya uyarı
    log "${YELLOW}UYARI: Bu işlem mevcut veriyi silecek ve yerine yedekten geri yükleyecektir.${NC}"
    read -p "Devam etmek istiyor musunuz? (e/h): " confirm
    
    if [[ "$confirm" != "e" && "$confirm" != "E" ]]; then
        log "${YELLOW}İşlem iptal edildi.${NC}"
        exit 0
    fi
    
    # Veritabanını geri yükle
    log "${GREEN}Veritabanı geri yükleniyor: ${DB_BACKUP}${NC}"
    
    # Mevcut veritabanını düşür ve yeniden oluştur
    if psql -h db -U $POSTGRES_USER -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"; then
        if psql -h db -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB;"; then
            # Veritabanını geri yükle
            if gunzip -c $DB_BACKUP | psql -h db -U $POSTGRES_USER $POSTGRES_DB; then
                log "${GREEN}Veritabanı başarıyla geri yüklendi.${NC}"
            else
                log "${RED}HATA: Veritabanı geri yüklenirken bir sorun oluştu.${NC}"
                exit 1
            fi
        else
            log "${RED}HATA: Veritabanı oluşturulamadı.${NC}"
            exit 1
        fi
    else
        log "${RED}HATA: Mevcut veritabanı kaldırılamadı.${NC}"
        exit 1
    fi
    
    # Medya dosyalarını geri yükle
    log "${GREEN}Medya dosyaları geri yükleniyor: ${MEDIA_BACKUP}${NC}"
    
    # Mevcut medya klasörünü temizle
    rm -rf /code/media/*
    
    # Medya dosyalarını geri yükle
    if tar -xzf $MEDIA_BACKUP -C /code/media; then
        log "${GREEN}Medya dosyaları başarıyla geri yüklendi.${NC}"
    else
        log "${RED}HATA: Medya dosyaları geri yüklenirken bir sorun oluştu.${NC}"
        exit 1
    fi
    
    # İzinleri ayarla
    log "${GREEN}Dosya izinleri ayarlanıyor...${NC}"
    find /code/media -type d -exec chmod 755 {} \;
    find /code/media -type f -exec chmod 644 {} \;
    
    # Geri yükleme özeti
    log "${GREEN}Geri yükleme işlemi tamamlandı.${NC}"
    log "${GREEN}Veritabanı ve medya dosyaları başarıyla geri yüklendi.${NC}"
    log "${YELLOW}Not: Değişikliklerin tam olarak uygulanması için Django uygulamasını yeniden başlatmanız gerekebilir.${NC}"
}

# Ana işlevi çalıştır
main "$@" 