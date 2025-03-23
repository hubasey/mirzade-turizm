# Mirzade Tur Web Sitesi

Mirzade Tur şirketi için geliştirilen web sitesi projesi.

## Özellikler

### Ana Sayfa
- Slider bölümü
- Kategori kartları (Hac, Umre, Kültür Turları)
- Öne çıkan turlar listesi
- Arama formu

### Tur Detay Sayfası
- Tur bilgileri (fiyat, tarih, süre, vb.)
- Tur programı
- Rezervasyon formu
- Benzer turlar bölümü

### Kategori Sayfası
- Seçilen kategoriye ait turların listelenmesi
- Filtreleme seçenekleri

### Arama Sayfası
- Gelişmiş arama ve filtreleme seçenekleri
- Sonuçların listelenmesi

### Hakkımızda Sayfası
- Şirket tanıtımı
- Misyon ve vizyon
- Şirket değerleri
- Ekip üyeleri
- Neden bizi seçmelisiniz bölümü

## Teknik Özellikler
- Django web framework
- Bootstrap 5 ile responsive tasarım
- FontAwesome ikonları
- Performans optimizasyonları
- SEO uyumlu yapı

## Kurulum

```bash
# Sanal ortam oluşturma
python -m venv venv

# Sanal ortamı aktifleştirme
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate

# Bağımlılıkları yükleme
pip install -r requirements.txt

# Veritabanı migrasyonlarını uygulama
python manage.py migrate

# Geliştirme sunucusunu başlatma
python manage.py runserver
```

## Docker ile Çalıştırma

```bash
# Docker container'ları oluşturma ve başlatma
docker-compose up -d

# Değişikliklerden sonra yeniden başlatma
docker-compose restart web
```

## Statik Dosyalar

Statik dosyalar (CSS, JavaScript, resimler vb.) aşağıdaki şekilde yapılandırılmıştır:

- `static/` klasörü: Geliştirme sırasında statik dosyaları buraya ekleyin
- `staticfiles/` klasörü: `collectstatic` komutu ile toplanan statik dosyalar burada saklanır
- Docker Compose, statik dosyaları bir Docker volume'unda saklar

Statik dosyaları manuel olarak toplamak için:

```
docker exec -it django_app python manage.py collectstatic
```

## Sorun Giderme

### Veritabanı Bağlantı Hatası

Eğer "could not translate host name 'db' to address: Name or service not known" hatası alırsanız:

1. Docker ağının doğru şekilde oluşturulduğundan emin olun:
   ```
   docker network ls
   ```

2. Konteynerler arasında iletişim olduğunu kontrol edin:
   ```
   docker-compose ps
   ```

3. Gerekirse konteynerlerinizi yeniden başlatın:
   ```
   docker-compose down
   docker-compose up --build
   ```

### Statik Dosya Hatası

Eğer "You're using the staticfiles app without having set the STATIC_ROOT setting to a filesystem path" hatası alırsanız:

1. `settings.py` dosyasında `STATIC_ROOT` ayarının doğru şekilde yapılandırıldığından emin olun
2. `static/` klasörünün projenizde var olduğundan emin olun
3. Docker Compose dosyasında statik dosyalar için bir volume tanımlandığından emin olun

### Pillow Kütüphanesi Hatası

Eğer "Cannot use ImageField because Pillow is not installed" hatası alırsanız:

1. `requirements.txt` dosyasında Pillow kütüphanesinin listelendiğinden emin olun
2. Docker imajını yeniden oluşturun:
   ```
   docker-compose down
   docker-compose up --build
   ```
3. Veya konteynere bağlanıp manuel olarak yükleyin:
   ```
   docker exec -it django_app pip install Pillow
   ```

### Windows Ortamında Docker Sorunları

Windows ortamında Docker kullanırken karşılaşabileceğiniz sorunlar için:

1. Docker Desktop'ın en son sürümünü kullandığınızdan emin olun

2. WSL 2 (Windows Subsystem for Linux) kullanıyorsanız, WSL entegrasyonunun Docker Desktop ayarlarında etkinleştirildiğinden emin olun

3. Docker komut satırı araçlarının PATH'e eklendiğinden emin olun

4. Dosya paylaşımı sorunları için Docker Desktop ayarlarında "Resources > File Sharing" bölümünü kontrol edin

## Veritabanı Yapılandırması

Veritabanı ayarları `core/settings.py` dosyasında ve `docker-compose.yml` dosyasında tanımlanmıştır:

- Veritabanı adı: `hac_db`
- Kullanıcı adı: `postgres`
- Şifre: `postgres`
- Host: `db`
- Port: `5432`

## Geliştirme

Yerel geliştirme için, `.env` dosyası oluşturarak veritabanı bağlantı bilgilerini değiştirebilirsiniz.

## Resmi Belgeler Ekleme

Anasayfada "Neden Mirzade Turizm?" bölümünde resmi belgeleri göstermek için aşağıdaki adımları izleyin:

1. Belge görüntülerini `mirzade/static/img/documents/` klasörüne yükleyin:
   - `belge1.jpg` - Diyanet İşleri Başkanlığı İzin Belgesi
   - `belge2.jpg` - TÜRSAB Belgesi
   - `belge3.jpg` - Suudi Arabistan Vize Yetkisi

2. PDF dosyalarını aynı klasöre yükleyin:
   - `belge1.pdf` - Diyanet İşleri Başkanlığı İzin Belgesi
   - `belge2.pdf` - TÜRSAB Belgesi
   - `belge3.pdf` - Suudi Arabistan Vize Yetkisi

3. Görüntüler ve PDF'ler yüklendikten sonra, statik dosyaları toplamak için aşağıdaki komutu çalıştırın:
   ```
   python manage.py collectstatic
   ```

4. Belge sayısını veya içeriğini değiştirmek isterseniz, `mirzade/main/templates/main/index.html` dosyasındaki "Resmi Belgeler Bölümü" kısmını düzenleyin.

Not: Belge görüntüleri için önerilen boyut: 800x600 piksel, JPG formatı. PDF dosyaları optimize edilmiş olmalıdır.

## Docker ile Kurulum ve Çalıştırma

Bu projeyi Docker ve Docker Compose kullanarak hem yerel geliştirme ortamında hem de sunucuda çalıştırabilirsiniz.

### Gereksinimler

- Docker
- Docker Compose

### Yerel Geliştirme Ortamında Çalıştırma

1. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullaniciadı/mirzade.git
   cd mirzade
   ```

2. `.env.example` dosyasını `.env` olarak kopyalayın ve gerekli değerleri güncelleyin:
   ```bash
   cp .env.example .env
   ```

3. Docker Compose ile geliştirme ortamını başlatın:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up
   ```

4. Tarayıcınızda `http://localhost:8000` adresine giderek uygulamayı görebilirsiniz.

### Üretim Ortamında Çalıştırma (Sunucu)

1. Projeyi sunucuya kopyalayın:
   ```bash
   git clone https://github.com/kullaniciadı/mirzade.git
   cd mirzade
   ```

2. `.env.example` dosyasını `.env` olarak kopyalayın ve üretim değerlerini güncelleyin:
   ```bash
   cp .env.example .env
   ```

3. Kurulum betiğini çalıştırın (Ubuntu/Debian tabanlı sistemler için):
   ```bash
   chmod +x deploy-server.sh
   sudo ./deploy-server.sh
   ```

4. Veya manuel olarak Docker Compose ile servisleri başlatın:
   ```bash
   docker-compose up -d
   ```

5. Tarayıcınızda sunucu adresine giderek uygulamayı görebilirsiniz.

### SSL/TLS Kurulumu

Canlı ortamda HTTPS kullanmak için:

1. `config/nginx/mirzade.conf` dosyasındaki HTTP yönlendirme satırının yorumunu kaldırın.
2. SSL yapılandırması ile ilgili yorum satırlarını kaldırın.
3. Let's Encrypt sertifikası alın:
   ```bash
   certbot certonly --webroot -w /var/www/certbot -d mirzadeturizm.com -d www.mirzadeturizm.com
   ```

## Görsel Sorunlarını Çözme

Eğer tur görselleri veya galeri görüntüleri görüntülenmiyorsa:

1. İzin düzeltme betiğini çalıştırın:
   ```bash
   chmod +x fix_permissions.sh
   ./fix_permissions.sh
   ```

2. Veya Docker konteynerinin içinde manuel olarak izinleri ayarlayın:
   ```bash
   docker exec -it mirzade_web_1 sh -c "chmod -R 755 /app/media"
   ``` 