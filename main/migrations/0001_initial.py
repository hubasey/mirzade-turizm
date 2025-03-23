# Generated by Django 5.1.6 on 2025-03-09 20:06

import django.db.models.deletion
import django_ckeditor_5.fields
import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlogCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Kategori Adı')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
            ],
            options={
                'verbose_name': 'Blog Kategorisi',
                'verbose_name_plural': 'Blog Kategorileri',
            },
        ),
        migrations.CreateModel(
            name='BlogTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Etiket Adı')),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'verbose_name': 'Blog Etiketi',
                'verbose_name_plural': 'Blog Etiketleri',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='HotelAmenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Özellik Adı')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='İkon Kodu')),
            ],
            options={
                'verbose_name': 'Otel Özelliği',
                'verbose_name_plural': 'Otel Özellikleri',
            },
        ),
        migrations.CreateModel(
            name='HotelCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Kategori Adı')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
            ],
            options={
                'verbose_name': 'Otel Kategorisi',
                'verbose_name_plural': 'Otel Kategorileri',
            },
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True, verbose_name='Başlık')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Açıklama')),
                ('image', main.models.OptimizedImageField(blank=True, null=True, upload_to='slider_images/', verbose_name='Resim')),
                ('url', models.URLField(blank=True, null=True, verbose_name='URL')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Sıralama')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
            ],
            options={
                'verbose_name': 'Slider',
                'verbose_name_plural': 'Sliderlar',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Başlık')),
                ('description', models.TextField(blank=True, default='', verbose_name='Açıklama')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Fiyat')),
                ('currency', models.CharField(default='TL', max_length=3, verbose_name='Para Birimi')),
                ('date', models.DateField(verbose_name='Tarih')),
                ('duration', models.PositiveIntegerField(help_text='Gün sayısı', verbose_name='Süre (Gün)')),
                ('image', models.ImageField(blank=True, null=True, upload_to='tour_images/', verbose_name='Tur Görseli')),
                ('category', models.CharField(choices=[('hac', 'Hac'), ('umre', 'Umre'), ('kultur', 'Kültür Turları')], max_length=10, verbose_name='Kategori')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                ('departure_city', models.CharField(blank=True, max_length=100, null=True)),
                ('arrival_city', models.CharField(blank=True, max_length=100, null=True)),
                ('departure_time', models.TimeField(blank=True, null=True)),
                ('arrival_time', models.TimeField(blank=True, null=True)),
                ('transportation_type', models.CharField(blank=True, choices=[('UCAK', 'Uçak'), ('OTOBUS', 'Otobüs'), ('GEMI', 'Gemi')], max_length=50, null=True)),
                ('double_room_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='İkili Oda Kişi Başı')),
                ('triple_room_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Üçlü Oda Kişi Başı')),
                ('quad_room_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Dörtlü Oda Kişi Başı')),
                ('latitude', models.FloatField(blank=True, null=True, verbose_name='Enlem')),
                ('longitude', models.FloatField(blank=True, null=True, verbose_name='Boylam')),
            ],
            options={
                'verbose_name': 'Tur',
                'verbose_name_plural': 'Turlar',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='TourActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Aktivite Adı')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Açıklama')),
                ('duration', models.CharField(blank=True, max_length=50, null=True, verbose_name='Süre')),
            ],
            options={
                'verbose_name': 'Tur Aktivitesi',
                'verbose_name_plural': 'Tur Aktiviteleri',
            },
        ),
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Başlık')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('content', django_ckeditor_5.fields.CKEditor5Field(verbose_name='İçerik')),
                ('summary', models.TextField(blank=True, verbose_name='Özet')),
                ('image', main.models.OptimizedImageField(blank=True, null=True, upload_to='blog_images/', verbose_name='Kapak Görseli')),
                ('author', models.CharField(default='Admin', max_length=100, verbose_name='Yazar')),
                ('published_date', models.DateTimeField(auto_now_add=True, verbose_name='Yayın Tarihi')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')),
                ('is_published', models.BooleanField(default=True, verbose_name='Yayında')),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='Görüntülenme')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='main.blogcategory', verbose_name='Kategori')),
                ('tags', models.ManyToManyField(blank=True, related_name='posts', to='main.blogtag', verbose_name='Etiketler')),
            ],
            options={
                'verbose_name': 'Blog Yazısı',
                'verbose_name_plural': 'Blog Yazıları',
                'ordering': ['-published_date'],
            },
        ),
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Ad Soyad')),
                ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                ('content', models.TextField(verbose_name='Yorum')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Onaylandı mı?')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='main.blogpost', verbose_name='Yazı')),
            ],
            options={
                'verbose_name': 'Blog Yorumu',
                'verbose_name_plural': 'Blog Yorumları',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Otel Adı')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField(verbose_name='Açıklama')),
                ('address', models.TextField(verbose_name='Adres')),
                ('city', models.CharField(max_length=100, verbose_name='Şehir')),
                ('country', models.CharField(max_length=100, verbose_name='Ülke')),
                ('star_rating', models.PositiveSmallIntegerField(choices=[(1, '1 Yıldız'), (2, '2 Yıldız'), (3, '3 Yıldız'), (4, '4 Yıldız'), (5, '5 Yıldız')], verbose_name='Yıldız Sayısı')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Enlem')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name='Boylam')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif mi?')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')),
                ('distance_to_haram', models.PositiveIntegerField(blank=True, null=True, verbose_name="Harem'e Uzaklık (metre)")),
                ('view_of_kaaba', models.BooleanField(default=False, verbose_name='Kabe Manzaralı')),
                ('view_of_haram', models.BooleanField(default=False, verbose_name='Harem Manzaralı')),
                ('has_prayer_room', models.BooleanField(default=False, verbose_name='Mescit')),
                ('has_quran', models.BooleanField(default=False, verbose_name='Kuran-ı Kerim')),
                ('has_qibla_direction', models.BooleanField(default=False, verbose_name='Kıble Yönü')),
                ('has_prayer_mat', models.BooleanField(default=False, verbose_name='Seccade')),
                ('has_haram_shuttle', models.BooleanField(default=False, verbose_name='Harem Servisi')),
                ('has_airport_shuttle', models.BooleanField(default=False, verbose_name='Havalimanı Servisi')),
                ('has_mina_shuttle', models.BooleanField(default=False, verbose_name='Mina Servisi')),
                ('has_arafat_shuttle', models.BooleanField(default=False, verbose_name='Arafat Servisi')),
                ('has_breakfast', models.BooleanField(default=False, verbose_name='Kahvaltı Dahil')),
                ('has_lunch', models.BooleanField(default=False, verbose_name='Öğle Yemeği Dahil')),
                ('has_dinner', models.BooleanField(default=False, verbose_name='Akşam Yemeği Dahil')),
                ('has_turkish_food', models.BooleanField(default=False, verbose_name='Türk Mutfağı')),
                ('suitable_for_hajj', models.BooleanField(default=False, verbose_name='Hac İçin Uygun')),
                ('has_mina_tent', models.BooleanField(default=False, verbose_name='Mina Çadırı Dahil')),
                ('has_arafat_tent', models.BooleanField(default=False, verbose_name='Arafat Çadırı Dahil')),
                ('has_turkish_guide', models.BooleanField(default=False, verbose_name='Türkçe Rehber')),
                ('has_religious_guide', models.BooleanField(default=False, verbose_name='Dini Rehberlik')),
                ('has_24h_assistance', models.BooleanField(default=False, verbose_name='24 Saat Destek')),
                ('has_zamzam', models.BooleanField(default=False, verbose_name='Zemzem Suyu')),
                ('has_ihram', models.BooleanField(default=False, verbose_name='İhram Dahil')),
                ('has_laundry', models.BooleanField(default=False, verbose_name='Çamaşırhane')),
                ('is_pet_friendly', models.BooleanField(default=False, verbose_name='Evcil Hayvan Dostu')),
                ('is_accessible', models.BooleanField(default=False, verbose_name='Engelli Dostu')),
                ('has_all_inclusive', models.BooleanField(default=False, verbose_name='Her Şey Dahil')),
                ('amenities', models.ManyToManyField(blank=True, to='main.hotelamenity', verbose_name='Özellikler')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.hotelcategory', verbose_name='Kategori')),
            ],
            options={
                'verbose_name': 'Otel',
                'verbose_name_plural': 'Oteller',
            },
        ),
        migrations.CreateModel(
            name='HotelImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='hotels/', verbose_name='Fotoğraf')),
                ('title', models.CharField(blank=True, max_length=100, verbose_name='Başlık')),
                ('is_main', models.BooleanField(default=False, verbose_name='Ana Fotoğraf mı?')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Sıralama')),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.hotel', verbose_name='Otel')),
            ],
            options={
                'verbose_name': 'Otel Fotoğrafı',
                'verbose_name_plural': 'Otel Fotoğrafları',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Oda Tipi')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                ('capacity', models.PositiveSmallIntegerField(default=2, verbose_name='Kapasite')),
                ('price_per_night', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Gecelik Fiyat')),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_types', to='main.hotel', verbose_name='Otel')),
            ],
            options={
                'verbose_name': 'Oda Tipi',
                'verbose_name_plural': 'Oda Tipleri',
            },
        ),
        migrations.CreateModel(
            name='TourFAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=300, verbose_name='Soru')),
                ('answer', models.TextField(verbose_name='Cevap')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Sıralama')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faqs', to='main.tour', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur SSS',
                'verbose_name_plural': 'Tur SSS',
                'ordering': ['tour', 'order'],
            },
        ),
        migrations.CreateModel(
            name='TourGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True, verbose_name='Başlık')),
                ('image', main.models.OptimizedImageField(upload_to='tour_gallery/', verbose_name='Resim')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Sıralama')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery', to='main.tour', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur Galerisi',
                'verbose_name_plural': 'Tur Galerileri',
                'ordering': ['tour', 'order'],
            },
        ),
        migrations.CreateModel(
            name='TourProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.PositiveIntegerField(verbose_name='Gün')),
                ('title', models.CharField(max_length=200, verbose_name='Başlık')),
                ('description', models.TextField(verbose_name='Açıklama')),
                ('accommodation', models.CharField(blank=True, max_length=200, null=True, verbose_name='Konaklama')),
                ('meals', models.CharField(choices=[('breakfast', 'Kahvaltı'), ('lunch', 'Öğle Yemeği'), ('dinner', 'Akşam Yemeği'), ('breakfast_lunch', 'Kahvaltı ve Öğle Yemeği'), ('breakfast_dinner', 'Kahvaltı ve Akşam Yemeği'), ('lunch_dinner', 'Öğle ve Akşam Yemeği'), ('all_inclusive', 'Tüm Öğünler Dahil'), ('none', 'Yemek Dahil Değil')], default='breakfast', max_length=20, verbose_name='Yemekler')),
                ('important_notes', models.TextField(blank=True, null=True, verbose_name='Önemli Notlar')),
                ('start_time', models.TimeField(blank=True, null=True, verbose_name='Başlangıç Saati')),
                ('end_time', models.TimeField(blank=True, null=True, verbose_name='Bitiş Saati')),
                ('location', models.CharField(blank=True, max_length=200, null=True, verbose_name='Konum')),
                ('activities', models.ManyToManyField(blank=True, related_name='programs', to='main.touractivity', verbose_name='Aktiviteler')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program', to='main.tour', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur Programı',
                'verbose_name_plural': 'Tur Programları',
                'ordering': ['tour', 'day'],
            },
        ),
        migrations.CreateModel(
            name='TourReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Ad Soyad')),
                ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                ('phone', models.CharField(max_length=20, verbose_name='Telefon')),
                ('participants', models.PositiveIntegerField(verbose_name='Katılımcı Sayısı')),
                ('room_type', models.CharField(choices=[('single', 'TEK KİŞİLİK ODA'), ('double', 'DÖRTLÜ ODA'), ('suite', 'SUİT ODA')], default='single', max_length=20, verbose_name='Oda Tipi')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notlar')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('status', models.CharField(choices=[('pending', 'Beklemede'), ('confirmed', 'Onaylandı'), ('cancelled', 'İptal Edildi')], default='pending', max_length=20, verbose_name='Durum')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='main.tour', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur Rezervasyonu',
                'verbose_name_plural': 'Tur Rezervasyonları',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TourReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Ad Soyad')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-posta')),
                ('rating', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Değerlendirme')),
                ('comment', models.TextField(verbose_name='Yorum')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Onaylandı')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='main.tour', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur Yorumu',
                'verbose_name_plural': 'Tur Yorumları',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TourTransportation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Tarih')),
                ('departure_city', models.CharField(max_length=100, verbose_name='Kalkış Şehri')),
                ('arrival_city', models.CharField(max_length=100, verbose_name='Varış Şehri')),
                ('departure_time', models.TimeField(verbose_name='Kalkış Saati')),
                ('arrival_time', models.TimeField(verbose_name='Varış Saati')),
                ('transportation_type', models.CharField(choices=[('UCAK', 'Uçak'), ('OTOBUS', 'Otobüs'), ('GEMI', 'Gemi')], default='UCAK', max_length=50, verbose_name='Ulaşım Tipi')),
                ('flight_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Uçuş Numarası')),
                ('airline', models.CharField(blank=True, max_length=100, null=True, verbose_name='Havayolu')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transportations', to='main.tour', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur Ulaşımı',
                'verbose_name_plural': 'Tur Ulaşımları',
                'ordering': ['date', 'departure_time'],
            },
        ),
        migrations.CreateModel(
            name='TourHotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nights', models.PositiveSmallIntegerField(default=1, verbose_name='Konaklama Süresi (Gece)')),
                ('is_default', models.BooleanField(default=False, verbose_name='Varsayılan mı?')),
                ('price_adjustment', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Fiyat Ayarlaması')),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotel_tours', to='main.hotel', verbose_name='Otel')),
                ('room_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.roomtype', verbose_name='Oda Tipi')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tour_hotels', to='main.tour', verbose_name='Tur')),
            ],
            options={
                'verbose_name': 'Tur Oteli',
                'verbose_name_plural': 'Tur Otelleri',
                'unique_together': {('tour', 'hotel')},
            },
        ),
    ]
