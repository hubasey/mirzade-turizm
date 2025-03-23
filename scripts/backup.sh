#!/bin/bash

# Renk tanımlamaları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Değişkenler
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="mirzade_backup_${TIMESTAMP}"
BACKUP_DIR=${BACKUP_DIR:-"/backups"}
KEEP_DAYS=${KEEP_BACKUPS_FOR:-7}

# Log fonksiyonu
log() {
    echo -e "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

# Ana yedekleme işlevi
main() {
    log "${GREEN}Mirzade Turizm yedekleme işlemi başlatılıyor...${NC}"
    
    # Yedekleme dizini kontrolü
    if [ ! -d "$BACKUP_DIR" ]; then
        log "${YELLOW}Yedekleme dizini ($BACKUP_DIR) bulunamadı. Oluşturuluyor...${NC}"
        mkdir -p $BACKUP_DIR
    fi
    
    # Yedekleme dizini yazılabilir mi?
    if [ ! -w "$BACKUP_DIR" ]; then
        log "${RED}HATA: Yedekleme dizinine ($BACKUP_DIR) yazma izni yok. Yedekleme işlemi iptal edildi.${NC}"
        exit 1
    fi
    
    # Veritabanı yedekleme
    log "${GREEN}Veritabanı yedekleniyor...${NC}"
    DB_BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}_db.sql.gz"
    
    if pg_dump -h db -U $POSTGRES_USER $POSTGRES_DB | gzip > $DB_BACKUP_PATH; then
        log "${GREEN}Veritabanı başarıyla yedeklendi: ${DB_BACKUP_PATH}${NC}"
    else
        log "${RED}HATA: Veritabanı yedeklenirken bir sorun oluştu.${NC}"
        exit 1
    fi
    
    # Medya dosyalarını yedekleme
    log "${GREEN}Medya dosyaları yedekleniyor...${NC}"
    MEDIA_BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}_media.tar.gz"
    
    if tar -czf $MEDIA_BACKUP_PATH -C /code/media .; then
        log "${GREEN}Medya dosyaları başarıyla yedeklendi: ${MEDIA_BACKUP_PATH}${NC}"
    else
        log "${RED}HATA: Medya dosyaları yedeklenirken bir sorun oluştu.${NC}"
    fi
    
    # Eski yedeklemeleri temizleme
    log "${GREEN}${KEEP_DAYS} günden eski yedeklemeler temizleniyor...${NC}"
    find $BACKUP_DIR -name "mirzade_backup_*" -type f -mtime +$KEEP_DAYS -delete
    
    # Yedekleme özeti
    log "${GREEN}Yedekleme işlemi tamamlandı.${NC}"
    log "${GREEN}Veritabanı yedek boyutu: $(du -h $DB_BACKUP_PATH | cut -f1)${NC}"
    
    if [ -f "$MEDIA_BACKUP_PATH" ]; then
        log "${GREEN}Medya yedek boyutu: $(du -h $MEDIA_BACKUP_PATH | cut -f1)${NC}"
    fi
    
    log "${GREEN}Toplam disk kullanımı: $(du -sh $BACKUP_DIR | cut -f1)${NC}"
}

# Ana işlevi çalıştır
main 