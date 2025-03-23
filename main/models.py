from django.db import models
from django.utils.text import slugify
from PIL import Image
import io
from django.core.files.base import ContentFile
import os
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse

class OptimizedImageField(models.ImageField):
    """
    Resimleri otomatik olarak optimize eden özel bir ImageField.
    """
    def __init__(self, max_width=None, max_height=None, *args, **kwargs):
        self.max_width = max_width
        self.max_height = max_height
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        file = super().pre_save(model_instance, add)
        if file and hasattr(file, 'name') and file.name:
            self.optimize_image(model_instance, file.name)
        return file

    def optimize_image(self, model_instance, file_name):
        # Eğer dosya adı zaten .webp ile bitiyorsa, optimize etme
        if file_name.lower().endswith('.webp'):
            # Dosya zaten optimize edilmiş olabilir
            return

        # Resim dosyasını kontrol et
        image_field = getattr(model_instance, self.attname)
        if not image_field:
            return
            
        try:
            # Resmi aç
            img = Image.open(image_field)
            
            # Boyutlandırma
            if self.max_width and self.max_height and (img.width > self.max_width or img.height > self.max_height):
                img.thumbnail((self.max_width, self.max_height), Image.LANCZOS)
            
            # WebP formatına dönüştür
            output = io.BytesIO()
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            
            # WebP olarak kaydet (daha düşük kalite)
            img.save(output, format='WEBP', quality=60, optimize=True)
            output.seek(0)
            
            # Dosya adını değiştir
            file_name_base, file_name_ext = os.path.splitext(file_name)
            new_file_name = f"{file_name_base}.webp"
            
            # Yeni dosyayı kaydet
            getattr(model_instance, self.attname).save(
                new_file_name,
                ContentFile(output.read()),
                save=False
            )
        except Exception as e:
            # Hata durumunda işlemi atla
            print(f"Resim optimizasyonu sırasında hata: {e}")
            pass

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Tour(models.Model):
    CATEGORY_CHOICES = (
        ('hac', 'Hac'),
        ('umre', 'Umre'),
        ('kultur', 'Kültür Turları'),
    )
    
    title = models.CharField(max_length=200, verbose_name="Başlık")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL")
    description = models.TextField(verbose_name="Açıklama", blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    currency = models.CharField(max_length=3, default="TL", verbose_name="Para Birimi")
    date = models.DateField(verbose_name="Tarih")
    duration = models.PositiveIntegerField(verbose_name="Süre (Gün)", help_text="Gün sayısı")
    image = OptimizedImageField(upload_to='tour_images/', blank=True, null=True, verbose_name="Tur Görseli", max_width=800, max_height=600)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name="Kategori")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # Lüks tur özellikleri
    is_luxury = models.BooleanField(default=False, verbose_name="Lüks Tur")
    luxury_features = models.TextField(blank=True, null=True, verbose_name="Lüks Özellikler", help_text="Her satıra bir özellik yazın")
    luxury_amenities = models.TextField(blank=True, null=True, verbose_name="Lüks Hizmetler", help_text="Her satıra bir hizmet yazın")
    vip_transfer = models.BooleanField(default=False, verbose_name="VIP Transfer")
    special_guide = models.BooleanField(default=False, verbose_name="Özel Rehber")
    
    # Eski ulaşım alanları (geriye dönük uyumluluk için tutuyoruz)
    departure_city = models.CharField(max_length=100, blank=True, null=True)
    arrival_city = models.CharField(max_length=100, blank=True, null=True)
    departure_time = models.TimeField(blank=True, null=True)
    arrival_time = models.TimeField(blank=True, null=True)
    transportation_type = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('UCAK', 'Uçak'),
        ('OTOBUS', 'Otobüs'),
        ('GEMI', 'Gemi'),
    ])
    
    # Oda tipi fiyatlandırması
    double_room_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="İkili Oda Kişi Başı")
    triple_room_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Üçlü Oda Kişi Başı")
    quad_room_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Dörtlü Oda Kişi Başı")
    
    # Harita koordinatları
    latitude = models.FloatField(blank=True, null=True, verbose_name="Enlem")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Boylam")
    
    class Meta:
        verbose_name = "Tur"
        verbose_name_plural = "Turlar"
        ordering = ['-date']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Başlıktan slug oluştur
            base_slug = slugify(self.title)
            # Eğer aynı slug varsa sonuna numara ekle
            counter = 1
            slug = base_slug
            while Tour.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tour_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

class TourTransportation(models.Model):
    """Tur için ulaşım bilgilerini tutan model"""
    TRANSPORTATION_TYPES = [
        ('UCAK', 'Uçak'),
        ('OTOBUS', 'Otobüs'),
        ('GEMI', 'Gemi'),
    ]
    
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='transportations', verbose_name="Tur")
    date = models.DateField(verbose_name="Tarih")
    departure_city = models.CharField(max_length=100, verbose_name="Kalkış Şehri")
    arrival_city = models.CharField(max_length=100, verbose_name="Varış Şehri")
    departure_time = models.TimeField(verbose_name="Kalkış Saati")
    arrival_time = models.TimeField(verbose_name="Varış Saati")
    transportation_type = models.CharField(max_length=50, choices=TRANSPORTATION_TYPES, default='UCAK', verbose_name="Ulaşım Tipi")
    flight_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Uçuş Numarası")
    airline = models.CharField(max_length=100, blank=True, null=True, verbose_name="Havayolu")
    
    class Meta:
        verbose_name = "Tur Ulaşımı"
        verbose_name_plural = "Tur Ulaşımları"
        ordering = ['date', 'departure_time']
    
    def __str__(self):
        return f"{self.date} - {self.departure_city} → {self.arrival_city}"

class Slider(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Başlık")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    image = OptimizedImageField(upload_to='slider_images/', verbose_name="Resim", null=True, blank=True, max_width=1000, max_height=600)
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliderlar"
        ordering = ['order']
    
    def __str__(self):
        return self.title if self.title else f"Slider {self.id}"

class TourActivity(models.Model):
    """Tur programındaki aktiviteler"""
    name = models.CharField(max_length=200, verbose_name="Aktivite Adı")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    duration = models.CharField(max_length=50, blank=True, null=True, verbose_name="Süre")
    
    class Meta:
        verbose_name = "Tur Aktivitesi"
        verbose_name_plural = "Tur Aktiviteleri"
    
    def __str__(self):
        return self.name

class TourProgram(models.Model):
    """Tur programı (günlük plan)"""
    MEAL_CHOICES = [
        ('breakfast', 'Kahvaltı'),
        ('lunch', 'Öğle Yemeği'),
        ('dinner', 'Akşam Yemeği'),
        ('breakfast_lunch', 'Kahvaltı ve Öğle Yemeği'),
        ('breakfast_dinner', 'Kahvaltı ve Akşam Yemeği'),
        ('lunch_dinner', 'Öğle ve Akşam Yemeği'),
        ('all_inclusive', 'Tüm Öğünler Dahil'),
        ('none', 'Yemek Dahil Değil'),
    ]
    
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='program', verbose_name="Tur")
    day = models.PositiveIntegerField(verbose_name="Gün")
    title = models.CharField(max_length=200, verbose_name="Başlık")
    description = models.TextField(verbose_name="Açıklama")
    activities = models.ManyToManyField(TourActivity, blank=True, related_name="programs", verbose_name="Aktiviteler")
    
    # Yeni alanlar
    accommodation = models.CharField(max_length=200, blank=True, null=True, verbose_name="Konaklama")
    meals = models.CharField(max_length=20, choices=MEAL_CHOICES, default='breakfast', blank=True, null=True, verbose_name="Yemekler")
    important_notes = models.TextField(blank=True, null=True, verbose_name="Önemli Notlar")
    start_time = models.TimeField(blank=True, null=True, verbose_name="Başlangıç Saati")
    end_time = models.TimeField(blank=True, null=True, verbose_name="Bitiş Saati")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="Konum")
    
    class Meta:
        verbose_name = "Tur Programı"
        verbose_name_plural = "Tur Programları"
        ordering = ['tour', 'day']
    
    def __str__(self):
        return f"{self.tour.title} - Gün {self.day}: {self.title}"

class TourReview(models.Model):
    """Tur yorumları"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews', verbose_name="Tur")
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)
    rating = models.PositiveIntegerField(verbose_name="Değerlendirme", choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    is_approved = models.BooleanField(default=False, verbose_name="Onaylandı")
    
    class Meta:
        verbose_name = "Tur Yorumu"
        verbose_name_plural = "Tur Yorumları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.tour.title}"

class TourFAQ(models.Model):
    """Tur ile ilgili sık sorulan sorular"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='faqs', verbose_name="Tur")
    question = models.CharField(max_length=300, verbose_name="Soru")
    answer = models.TextField(verbose_name="Cevap")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    
    class Meta:
        verbose_name = "Tur SSS"
        verbose_name_plural = "Tur SSS"
        ordering = ['tour', 'order']
    
    def __str__(self):
        return f"{self.tour.title} - {self.question[:50]}"

class TourGallery(models.Model):
    """Tur fotoğraf galerisi"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='gallery', verbose_name="Tur")
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Başlık")
    image = OptimizedImageField(upload_to='tour_gallery/', verbose_name="Resim", max_width=800, max_height=600)
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    
    class Meta:
        verbose_name = "Tur Galerisi"
        verbose_name_plural = "Tur Galerileri"
        ordering = ['tour', 'order']
    
    def __str__(self):
        return f"{self.tour.title} - {self.title or 'Resim'}"

# Oda tipleri seçenekleri
ROOM_TYPES = [
    ('double', 'İKİ KİŞİLİK ODA'),
    ('triple', 'ÜÇ KİŞİLİK ODA'),
    ('quad', 'DÖRT KİŞİLİK ODA'),
]

class TourReservation(models.Model):
    """Tur rezervasyonları"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reservations', verbose_name="Tur")
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    participants = models.PositiveIntegerField(verbose_name="Katılımcı Sayısı")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='double', verbose_name="Oda Tipi")
    notes = models.TextField(blank=True, null=True, verbose_name="Notlar")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    status = models.CharField(max_length=20, default="pending", choices=[
        ('pending', 'Beklemede'),
        ('confirmed', 'Onaylandı'),
        ('cancelled', 'İptal Edildi'),
    ], verbose_name="Durum")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Fiyat", null=True, blank=True)
    total_persons = models.PositiveIntegerField(verbose_name="Toplam Kişi Sayısı", null=True, blank=True)
    
    class Meta:
        verbose_name = "Tur Rezervasyonu"
        verbose_name_plural = "Tur Rezervasyonları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.tour.title}"

class HotelCategory(models.Model):
    """Otel kategorilerini tanımlayan model"""
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Otel Kategorisi"
        verbose_name_plural = "Otel Kategorileri"

class HotelAmenity(models.Model):
    """Otel özelliklerini tanımlayan model"""
    name = models.CharField(max_length=100, verbose_name="Özellik Adı")
    icon = models.CharField(max_length=50, blank=True, verbose_name="İkon Kodu")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Otel Özelliği"
        verbose_name_plural = "Otel Özellikleri"

class Hotel(models.Model):
    """Otelleri tanımlayan ana model"""
    name = models.CharField(max_length=200, verbose_name="Otel Adı")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Açıklama")
    address = models.TextField(verbose_name="Adres")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    country = models.CharField(max_length=100, verbose_name="Ülke")
    star_rating = models.PositiveSmallIntegerField(verbose_name="Yıldız Sayısı", choices=[(i, f"{i} Yıldız") for i in range(1, 6)])
    category = models.ForeignKey(HotelCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategori")
    amenities = models.ManyToManyField(HotelAmenity, blank=True, verbose_name="Özellikler")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Enlem")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Boylam")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    # Hac ve Umre özellikleri
    distance_to_haram = models.PositiveIntegerField(null=True, blank=True, 
                                                  verbose_name="Harem'e Uzaklık (metre)")
    view_of_kaaba = models.BooleanField(default=False, verbose_name="Kabe Manzaralı")
    view_of_haram = models.BooleanField(default=False, verbose_name="Harem Manzaralı")
    has_prayer_room = models.BooleanField(default=False, verbose_name="Mescit")
    has_quran = models.BooleanField(default=False, verbose_name="Kuran-ı Kerim")
    has_qibla_direction = models.BooleanField(default=False, verbose_name="Kıble Yönü")
    has_prayer_mat = models.BooleanField(default=False, verbose_name="Seccade")
    
    # Ulaşım özellikleri
    has_haram_shuttle = models.BooleanField(default=False, verbose_name="Harem Servisi")
    has_airport_shuttle = models.BooleanField(default=False, verbose_name="Havalimanı Servisi")
    has_mina_shuttle = models.BooleanField(default=False, verbose_name="Mina Servisi")
    has_arafat_shuttle = models.BooleanField(default=False, verbose_name="Arafat Servisi")
    
    # Yemek özellikleri
    has_breakfast = models.BooleanField(default=False, verbose_name="Kahvaltı Dahil")
    has_lunch = models.BooleanField(default=False, verbose_name="Öğle Yemeği Dahil")
    has_dinner = models.BooleanField(default=False, verbose_name="Akşam Yemeği Dahil")
    has_turkish_food = models.BooleanField(default=False, verbose_name="Türk Mutfağı")
    
    # Hac dönemi özellikleri
    suitable_for_hajj = models.BooleanField(default=False, verbose_name="Hac İçin Uygun")
    has_mina_tent = models.BooleanField(default=False, verbose_name="Mina Çadırı Dahil")
    has_arafat_tent = models.BooleanField(default=False, verbose_name="Arafat Çadırı Dahil")
    
    # Rehberlik hizmetleri
    has_turkish_guide = models.BooleanField(default=False, verbose_name="Türkçe Rehber")
    has_religious_guide = models.BooleanField(default=False, verbose_name="Dini Rehberlik")
    has_24h_assistance = models.BooleanField(default=False, verbose_name="24 Saat Destek")
    
    # Ek hizmetler
    has_zamzam = models.BooleanField(default=False, verbose_name="Zemzem Suyu")
    has_ihram = models.BooleanField(default=False, verbose_name="İhram Dahil")
    has_laundry = models.BooleanField(default=False, verbose_name="Çamaşırhane")
    is_accessible = models.BooleanField(default=False, verbose_name="Engelli Dostu")
    has_all_inclusive = models.BooleanField(default=False, verbose_name="Her Şey Dahil")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"
    
    class Meta:
        verbose_name = "Otel"
        verbose_name_plural = "Oteller"

class HotelImage(models.Model):
    """Otel fotoğraflarını tanımlayan model"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="images", verbose_name="Otel")
    image = models.ImageField(upload_to="hotels/", verbose_name="Fotoğraf")
    title = models.CharField(max_length=100, blank=True, verbose_name="Başlık")
    is_main = models.BooleanField(default=False, verbose_name="Ana Fotoğraf mı?")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Sıralama")
    
    def __str__(self):
        return f"{self.hotel.name} - {self.title or 'Fotoğraf'}"
    
    class Meta:
        verbose_name = "Otel Fotoğrafı"
        verbose_name_plural = "Otel Fotoğrafları"
        ordering = ["order", "id"]

class RoomType(models.Model):
    """Oda tiplerini tanımlayan model"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="room_types", verbose_name="Otel")
    name = models.CharField(max_length=100, verbose_name="Oda Tipi")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    capacity = models.PositiveSmallIntegerField(default=2, verbose_name="Kapasite")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Gecelik Fiyat")
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"
    
    class Meta:
        verbose_name = "Oda Tipi"
        verbose_name_plural = "Oda Tipleri"

class TourHotel(models.Model):
    """Tur ve otel arasındaki ilişkiyi tanımlayan model"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='tour_hotels', verbose_name="Tur")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_tours', verbose_name="Otel")
    nights = models.PositiveSmallIntegerField(default=1, verbose_name="Konaklama Süresi (Gece)")
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Oda Tipi")
    is_default = models.BooleanField(default=False, verbose_name="Varsayılan mı?")
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Fiyat Ayarlaması")
    
    def __str__(self):
        return f"{self.tour.title} - {self.hotel.name} ({self.nights} gece)"
    
    class Meta:
        verbose_name = "Tur Oteli"
        verbose_name_plural = "Tur Otelleri"
        unique_together = ('tour', 'hotel')

# Blog Modelleri
class BlogCategory(models.Model):
    """Blog kategorilerini tanımlayan model"""
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Açıklama")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Blog Kategorisi"
        verbose_name_plural = "Blog Kategorileri"

class BlogTag(models.Model):
    """Blog etiketlerini tanımlayan model"""
    name = models.CharField(max_length=50, verbose_name="Etiket Adı")
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Blog Etiketi"
        verbose_name_plural = "Blog Etiketleri"

class BlogPost(models.Model):
    """Blog yazılarını tanımlayan model"""
    title = models.CharField(max_length=200, verbose_name="Başlık")
    slug = models.SlugField(unique=True, blank=True)
    content = CKEditor5Field(verbose_name="İçerik", config_name='default')
    summary = models.TextField(verbose_name="Özet", blank=True)
    image = OptimizedImageField(upload_to='blog_images/', verbose_name="Kapak Görseli", blank=True, null=True, max_width=800, max_height=600)
    category = models.ForeignKey('BlogCategory', on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name="Kategori")
    tags = models.ManyToManyField('BlogTag', blank=True, related_name='posts', verbose_name="Etiketler")
    author = models.CharField(max_length=100, verbose_name="Yazar", default="Admin")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Yayın Tarihi")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="Güncelleme Tarihi")
    is_published = models.BooleanField(default=True, verbose_name="Yayında")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme")
    
    class Meta:
        verbose_name = "Blog Yazısı"
        verbose_name_plural = "Blog Yazıları"
        ordering = ['-published_date']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class BlogComment(models.Model):
    """Blog yorumlarını tanımlayan model"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments", verbose_name="Yazı")
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    content = models.TextField(verbose_name="Yorum")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    is_approved = models.BooleanField(default=False, verbose_name="Onaylandı mı?")
    
    def __str__(self):
        return f"{self.name} - {self.post.title}"
    
    class Meta:
        verbose_name = "Blog Yorumu"
        verbose_name_plural = "Blog Yorumları"
        ordering = ['-created_date']

class SiteSettings(models.Model):
    """Site genelinde kullanılan ayarlar."""
    site_title = models.CharField(max_length=100, verbose_name="Site Başlığı")
    site_description = models.TextField(verbose_name="Site Açıklaması")
    logo = OptimizedImageField(upload_to='site_settings/', verbose_name="Logo", max_width=300, max_height=100)
    favicon = OptimizedImageField(upload_to='site_settings/', verbose_name="Favicon", max_width=64, max_height=64)
    
    # İletişim Bilgileri
    email = models.EmailField(verbose_name="E-posta")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    whatsapp = models.CharField(max_length=20, verbose_name="WhatsApp")
    address = models.TextField(verbose_name="Adres")
    
    # Sosyal Medya
    facebook = models.URLField(blank=True, null=True, verbose_name="Facebook")
    twitter = models.URLField(blank=True, null=True, verbose_name="Twitter")
    instagram = models.URLField(blank=True, null=True, verbose_name="Instagram")
    youtube = models.URLField(blank=True, null=True, verbose_name="YouTube")
    linkedin = models.URLField(blank=True, null=True, verbose_name="LinkedIn")
    
    # SEO Ayarları
    meta_keywords = models.TextField(blank=True, null=True, verbose_name="Meta Anahtar Kelimeler")
    meta_description = models.TextField(blank=True, null=True, verbose_name="Meta Açıklama")
    google_analytics = models.CharField(max_length=50, blank=True, null=True, verbose_name="Google Analytics ID")
    
    # Diğer Ayarlar
    footer_text = models.TextField(blank=True, null=True, verbose_name="Alt Bilgi Metni")
    copyright_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="Telif Hakkı Metni")
    
    class Meta:
        verbose_name = "Site Ayarları"
        verbose_name_plural = "Site Ayarları"
    
    def __str__(self):
        return self.site_title
    
    def save(self, *args, **kwargs):
        # Sadece bir kayıt olmasını sağla
        if not self.pk and SiteSettings.objects.exists():
            return
        return super().save(*args, **kwargs)