#!/bin/bash
# Mirzade Turizm Otomatik Yedekleme Betiği

# Yedekleme tarihi
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/var/backups/mirzade"

# Yedekleme dizini oluşturma
mkdir -p $BACKUP_DIR

# Veritabanı yedekleme
echo "PostgreSQL veritabanı yedekleniyor..."
docker exec mirzade-db-1 pg_dump -U ${DATABASE_USER:-mirzade_user} ${DATABASE_NAME:-mirzade_db} > $BACKUP_DIR/mirzade_db_$DATE.sql

# Medya dosyalarını yedekleme
echo "Medya dosyaları yedekleniyor..."
tar -zcf $BACKUP_DIR/mirzade_media_$DATE.tar.gz ./media

# Redis verilerini yedekleme
echo "Redis verileri yedekleniyor..."
docker exec mirzade-redis-1 redis-cli save
docker exec mirzade-redis-1 cat /data/dump.rdb > $BACKUP_DIR/mirzade_redis_$DATE.rdb

# Yedekleme tamamlandı
echo "Yedekleme tamamlandı: $BACKUP_DIR"
echo "  - Veritabanı: mirzade_db_$DATE.sql"
echo "  - Medya: mirzade_media_$DATE.tar.gz"
echo "  - Redis: mirzade_redis_$DATE.rdb"

# 30 günden eski yedekleri temizleme
echo "30 günden eski yedekleri temizleme..."
find $BACKUP_DIR -name "mirzade_db_*.sql" -type f -mtime +30 -delete
find $BACKUP_DIR -name "mirzade_media_*.tar.gz" -type f -mtime +30 -delete
find $BACKUP_DIR -name "mirzade_redis_*.rdb" -type f -mtime +30 -delete

echo "Yedekleme işlemi tamamlandı." 