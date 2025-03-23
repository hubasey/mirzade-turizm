# Mirzade Turizm Uygulaması Kurulum Rehberi

Bu rehber, Mirzade Turizm Django uygulamasının Ubuntu 20.04+ bir sunucuya kurulması için adım adım talimatlar içerir.

## Sistem Gereksinimleri

- Ubuntu 20.04 LTS veya daha yüksek
- En az 2GB RAM
- En az 1 CPU çekirdeği
- En az 20GB disk alanı
- Bir domain adresi (örn. mirzadeturizm.com)

## 1. Sunucu Hazırlığı

### 1.1 Sunucuya Bağlanma

SSH kullanarak sunucunuza bağlanın:

```bash
ssh kullanici@sunucu_ip
```

### 1.2 Kullanıcı Oluşturma (opsiyonel)

Güvenlik için root kullanıcısı yerine sudo yetkileri olan bir kullanıcı oluşturabilirsiniz:

```bash
adduser mirzade
usermod -aG sudo mirzade
```

SSH anahtarlarını ayarlayın:

```bash
mkdir -p /home/mirzade/.ssh
cp ~/.ssh/authorized_keys /home/mirzade/.ssh/
chown -R mirzade:mirzade /home/mirzade/.ssh
chmod 700 /home/mirzade/.ssh
chmod 600 /home/mirzade/.ssh/authorized_keys
```

### 1.3 Sunucu Saatini Ayarlama

```bash
sudo timedatectl set-timezone Europe/Istanbul
```

## 2. Repo Transferi

Uygulamayı sunucunuza aktarmak için iki yöntem var:

### 2.1 Git Kullanarak

```bash
# Dizini oluşturun
sudo mkdir -p /opt/mirzade
sudo chown -R $USER:$USER /opt/mirzade

# Repoyu klonlayın
git clone https://github.com/hubasey/mirzade-turizm.git /opt/mirzade
cd /opt/mirzade
```

### 2.2 Manuel Dosya Transferi

Alternatif olarak, dosyaları bilgisayarınızdan SCP ile aktarabilirsiniz:

```bash
# Bilgisayarınızda
scp -r ./mirzade kullanici@sunucu_ip:/tmp/

# Sunucuda
sudo mkdir -p /opt/mirzade
sudo mv /tmp/mirzade/* /opt/mirzade/
sudo chown -R $USER:$USER /opt/mirzade
```

## 3. Otomatik Kurulum

Kurulum işlemi için hazırladığımız betik tüm gerekli adımları otomatik olarak gerçekleştirecektir:

```bash
cd /opt/mirzade
chmod +x scripts/setup.sh
sudo ./scripts/setup.sh
```

Bu betik şunları yapacaktır:
- Sistem güncellemesi
- Gerekli paketlerin kurulumu (curl, git, apt-transport-https vb.)
- Docker ve Docker Compose kurulumu
- Firewall (UFW) yapılandırması
- Fail2ban kurulumu ve yapılandırması
- Dizin yapısı oluşturma
- Çevresel değişkenleri kontrol etme

## 4. Manuel Kurulum (Otomatik kurulum başarısız olursa)

### 4.1 Sistem Güncellemesi

```bash
sudo apt update && sudo apt upgrade -y
```

### 4.2 Gerekli Paketleri Kurma

```bash
sudo apt install -y curl git software-properties-common apt-transport-https ca-certificates gnupg lsb-release ufw fail2ban
```

### 4.3 Docker Kurulumu

```bash
# Docker GPG anahtarını ekle
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker repo ekle
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker kur
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Docker grubuna kullanıcıyı ekle
sudo usermod -aG docker $USER
```

### 4.4 Docker Compose Kurulumu

```bash
# Docker Compose'un son sürümünü indir
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Çalıştırma izni ver
sudo chmod +x /usr/local/bin/docker-compose
```

### 4.5 Firewall Yapılandırması

```bash
# Varsayılan politikaları ayarla
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH, HTTP ve HTTPS için port aç
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Firewall'u etkinleştir
sudo ufw enable
```

### 4.6 Fail2ban Yapılandırması

```bash
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Konfigürasyon dosyasını oluştur
sudo bash -c 'cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
EOF'

# Servisi yeniden başlat
sudo systemctl restart fail2ban
```

## 5. Uygulama Yapılandırması

### 5.1 Çevresel Değişkenleri Ayarlama

```bash
cd /opt/mirzade
cp .env.prod.example .env.prod
nano .env.prod  # Değişkenleri düzenleyin
```

Aşağıdaki değişkenleri kendi değerlerinizle güncelleyin:
- `SECRET_KEY`: Güvenli bir rastgele dize
- `ALLOWED_HOSTS`: Sitenizin domain adresini ekleyin
- `POSTGRES_PASSWORD`: Güçlü bir veritabanı şifresi
- `EMAIL_*`: E-posta yapılandırması için gerekli bilgiler

### 5.2 Uygulamayı Başlatma

```bash
cd /opt/mirzade
docker-compose -f docker-compose.prod.yml up -d
```

### 5.3 SSL Sertifikası Alma

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d mirzadeturizm.com -d www.mirzadeturizm.com --email admin@mirzadeturizm.com --agree-tos --no-eff-email
```

### 5.4 Tüm Servisleri Yeniden Başlatma

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 6. DNS ve Cloudflare Ayarları

Aşağıdaki DNS kayıtlarını eklemeniz gerekiyor:

| Tür  | Ad                 | İçerik           | TTL    | Proxy Durumu |
|------|--------------------| -----------------|--------|--------------|
| A    | mirzadeturizm.com  | [Sunucu IP]      | Auto   | Proxied      |
| A    | www                | [Sunucu IP]      | Auto   | Proxied      |
| CNAME| *                  | mirzadeturizm.com| Auto   | Proxied      |

Cloudflare'de SSL/TLS ayarları:
1. SSL/TLS > Overview: Full (strict) mod seçin
2. SSL/TLS > Edge Certificates: Tüm özellikleri etkinleştirin

## 7. Otomatik Yedekleme

Yedekleme betiği `/opt/mirzade/scripts/backup.sh` konumunda bulunur ve cron görevleri aracılığıyla otomatik olarak çalışır.

Manuel yedek almak için:

```bash
cd /opt/mirzade
./scripts/backup.sh
```

## 8. Bakım ve İzleme

### 8.1 Güncellemeler

Uygulamayı güncellemek için:

```bash
cd /opt/mirzade
./scripts/deploy.sh
```

### 8.2 Log Kontrolü

```bash
# Nginx logları
docker-compose -f docker-compose.prod.yml logs nginx

# Django uygulama logları
docker-compose -f docker-compose.prod.yml logs web
```

## 9. Sorun Giderme

### 9.1 Bağlantı Sorunları

SSL sorunları için:
```bash
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs certbot
```

### 9.2 Veritabanı Sorunları

```bash
# Veritabanı konteynerine bağlanma
docker-compose -f docker-compose.prod.yml exec db psql -U postgres
```

### 9.3 SSL Sertifika Sorunları

SSL sertifikasının yenilenmesinde sorun varsa:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot renew
```

## 10. Güvenlik Önerileri

1. Düzenli olarak sistem güncellemelerini yapın
2. Admin paneline erişimi IP adresine göre kısıtlayın
3. SSH bağlantılarını anahtar tabanlı kimlik doğrulama ile yapılandırın
4. Fail2ban ve UFW'u aktif tutun
5. Düzenli olarak yedekleme alın ve yedeklerin çalıştığını test edin

---

Sorun veya sorularınız için: admin@mirzadeturizm.com 