from django.shortcuts import render, get_object_or_404, redirect
from .models import Tour,Slider, TourTransportation, Category, TourReservation, ROOM_TYPES, Hotel, HotelCategory, HotelAmenity, BlogPost, BlogCategory, BlogTag, BlogComment
from django.db.models import Q, Count
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from photologue.models import Gallery
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db import connections
from django.db.utils import OperationalError
from redis.exceptions import RedisError
import redis
import os
import logging
import traceback
from django.views.decorators.http import require_POST

def home(request):
    """Ana sayfa: Tüm turlar ve slider görüntülenir."""
    # Aktif sliderları getir
    sliders = Slider.objects.filter(is_active=True).order_by("order")
    
    # Eğer slider yoksa, boş liste kullan
    if not sliders.exists():
        sliders = []
    
    tours = Tour.objects.all().order_by('-date')
    
    # Kalkış şehirlerini veritabanından çek
    departure_cities = TourTransportation.objects.values_list('departure_city', flat=True).distinct().order_by('departure_city')
    
    # Eski model alanlarından da kalkış şehirlerini çek
    old_departure_cities = Tour.objects.exclude(departure_city__isnull=True).exclude(departure_city='').values_list('departure_city', flat=True).distinct()
    
    # İki listeyi birleştir ve tekrar eden şehirleri kaldır
    all_departure_cities = list(set(list(departure_cities) + list(old_departure_cities)))
    all_departure_cities.sort()
    
    # Varış şehirlerini veritabanından çek
    arrival_cities = TourTransportation.objects.values_list('arrival_city', flat=True).distinct().order_by('arrival_city')
    
    # Eski model alanlarından da varış şehirlerini çek
    old_arrival_cities = Tour.objects.exclude(arrival_city__isnull=True).exclude(arrival_city='').values_list('arrival_city', flat=True).distinct()
    
    # İki listeyi birleştir ve tekrar eden şehirleri kaldır
    all_arrival_cities = list(set(list(arrival_cities) + list(old_arrival_cities)))
    all_arrival_cities.sort()
    
    # Benzersiz gün sayılarını veritabanından çek
    durations = Tour.objects.values_list('duration', flat=True).distinct().order_by('duration')
    
    # Bugünün tarihini context'e ekle
    today_date = datetime.now().date()
    
    return render(request, 'main/index.html', {
        'tours': tours, 
        'sliders': sliders, 
        'selected_category': None,
        'departure_cities': all_departure_cities,
        'arrival_cities': all_arrival_cities,
        'durations': durations,
        'today_date': today_date
    })

def category_filter(request, category):
    """Seçilen kategoriye göre turları filtreler."""
    tours = Tour.objects.filter(category=category).order_by('-date')
    
    # Kalkış şehirlerini veritabanından çek
    departure_cities = TourTransportation.objects.values_list('departure_city', flat=True).distinct().order_by('departure_city')
    
    # Eski model alanlarından da kalkış şehirlerini çek
    old_departure_cities = Tour.objects.exclude(departure_city__isnull=True).exclude(departure_city='').values_list('departure_city', flat=True).distinct()
    
    # İki listeyi birleştir ve tekrar eden şehirleri kaldır
    all_departure_cities = list(set(list(departure_cities) + list(old_departure_cities)))
    all_departure_cities.sort()
    
    # Varış şehirlerini veritabanından çek
    arrival_cities = TourTransportation.objects.values_list('arrival_city', flat=True).distinct().order_by('arrival_city')
    
    # Eski model alanlarından da varış şehirlerini çek
    old_arrival_cities = Tour.objects.exclude(arrival_city__isnull=True).exclude(arrival_city='').values_list('arrival_city', flat=True).distinct()
    
    # İki listeyi birleştir ve tekrar eden şehirleri kaldır
    all_arrival_cities = list(set(list(arrival_cities) + list(old_arrival_cities)))
    all_arrival_cities.sort()
    
    # Benzersiz gün sayılarını veritabanından çek
    durations = Tour.objects.values_list('duration', flat=True).distinct().order_by('duration')
    
    # Bugünün tarihini context'e ekle
    today_date = datetime.now().date()
    
    return render(request, 'main/index.html', {
        'tours': tours, 
        'selected_category': category,
        'departure_cities': all_departure_cities,
        'arrival_cities': all_arrival_cities,
        'durations': durations,
        'today_date': today_date
    })

def tour_detail(request, slug):
    """Seçilen turu detaylı gösterir."""
    tour = get_object_or_404(Tour, slug=slug)
    
    # Benzer turları bul (aynı kategoriden, ama farklı ID'ye sahip)
    similar_tours = Tour.objects.filter(category=tour.category).exclude(id=tour.id).order_by('-date')[:3]
    
    return render(request, 'main/tour_detail.html', {
        'tour': tour,
        'similar_tours': similar_tours
    })

def search_tours(request):
    """Tur arama işlevselliği."""
    tours = Tour.objects.filter(is_active=True)
    
    # Kalkış şehri filtresi
    departure_city = request.GET.get('departure_city')
    if departure_city:
        # Ana modeldeki kalkış şehri veya ulaşım bilgilerindeki kalkış şehri
        tours = tours.filter(
            Q(departure_city=departure_city) | 
            Q(transportations__departure_city=departure_city)
        ).distinct()
    
    # Varış şehri filtresi
    arrival_city = request.GET.get('arrival_city')
    if arrival_city:
        # Ana modeldeki varış şehri veya ulaşım bilgilerindeki varış şehri
        tours = tours.filter(
            Q(arrival_city=arrival_city) | 
            Q(transportations__arrival_city=arrival_city)
        ).distinct()
    
    # Kategori filtresi
    category = request.GET.get('category')
    if category:
        tours = tours.filter(category=category)
    
    # Süre filtresi
    duration = request.GET.get('duration')
    if duration:
        try:
            days = int(duration)
            tours = tours.filter(duration=days)
        except (ValueError, AttributeError):
            pass
    
    # Tarih aralığı filtresi
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            tours = tours.filter(date__gte=start_date)
        except (ValueError, TypeError):
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            tours = tours.filter(date__lte=end_date)
        except (ValueError, TypeError):
            pass
    
    # Tur no filtresi
    tour_no = request.GET.get('tour_no')
    if tour_no:
        tours = tours.filter(id=tour_no)
    
    # Fiyat aralığı filtresi
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    currency = request.GET.get('currency', 'TRY')
    
    if min_price:
        try:
            min_price = float(min_price)
            tours = tours.filter(price__gte=min_price, currency=currency)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            tours = tours.filter(price__lte=max_price, currency=currency)
        except (ValueError, TypeError):
            pass
    
    # Kalkış şehirlerini veritabanından çek
    departure_cities = TourTransportation.objects.values_list('departure_city', flat=True).distinct().order_by('departure_city')
    
    # Eski model alanlarından da kalkış şehirlerini çek
    old_departure_cities = Tour.objects.exclude(departure_city__isnull=True).exclude(departure_city='').values_list('departure_city', flat=True).distinct()
    
    # İki listeyi birleştir ve tekrar eden şehirleri kaldır
    all_departure_cities = list(set(list(departure_cities) + list(old_departure_cities)))
    all_departure_cities.sort()
    
    # Varış şehirlerini veritabanından çek
    arrival_cities = TourTransportation.objects.values_list('arrival_city', flat=True).distinct().order_by('arrival_city')
    
    # Eski model alanlarından da varış şehirlerini çek
    old_arrival_cities = Tour.objects.exclude(arrival_city__isnull=True).exclude(arrival_city='').values_list('arrival_city', flat=True).distinct()
    
    # İki listeyi birleştir ve tekrar eden şehirleri kaldır
    all_arrival_cities = list(set(list(arrival_cities) + list(old_arrival_cities)))
    all_arrival_cities.sort()
    
    # Benzersiz gün sayılarını veritabanından çek
    durations = Tour.objects.values_list('duration', flat=True).distinct().order_by('duration')
    
    # Bugünün tarihini context'e ekle
    today_date = datetime.now().date()
    
    return render(request, 'main/search_results.html', {
        'tours': tours,
        'departure_cities': all_departure_cities,
        'arrival_cities': all_arrival_cities,
        'durations': durations,
        'today_date': today_date,
        'search_params': request.GET,
    })

def tour_reservation(request, slug):
    """Tur rezervasyonu işleme."""
    tour = get_object_or_404(Tour, slug=slug)
    
    if request.method == 'POST':
        # Form verilerini al
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        room_type = request.POST.get('room_type')
        notes = request.POST.get('notes')
        
        # Oda tipine göre fiyat hesaplama
        room_prices = {
            'double': tour.double_room_price or tour.price,
            'triple': tour.triple_room_price or tour.price,
            'quad': tour.quad_room_price or tour.price
        }
        room_persons = {'double': 2, 'triple': 3, 'quad': 4}
        
        selected_price = room_prices.get(room_type, tour.price)
        total_persons = room_persons.get(room_type, 2)
        total_price = selected_price * total_persons
        
        try:
            # Rezervasyon veritabanına kaydediliyor
            reservation = TourReservation.objects.create(
                tour=tour,
                name=name,
                email=email,
                phone=phone,
                room_type=room_type,
                notes=notes,
                total_price=total_price,
                total_persons=total_persons,
                participants=total_persons  # Katılımcı sayısını ekledik
            )
            
            # Email içeriğini hazırla
            context = {
                'reservation': reservation,
                'tour': tour,
                'total_price': total_price,
                'room_type': dict(ROOM_TYPES).get(room_type, 'Belirtilmemiş'),
                'room_types': ROOM_TYPES
            }
            
            try:
                # Müşteriye email gönder
                customer_html = render_to_string('main/email/reservation_confirmation.html', context)
                customer_text = strip_tags(customer_html)
                
                send_mail(
                    subject=f'Mirzade Turizm - {tour.title} Rezervasyon Onayı',
                    message=customer_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=customer_html,
                    fail_silently=False,
                )
                
                # Yöneticiye email gönder
                admin_html = render_to_string('main/email/reservation_notification.html', context)
                admin_text = strip_tags(admin_html)
                
                send_mail(
                    subject=f'Yeni Tur Rezervasyonu - {tour.title}',
                    message=admin_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['mirzadeturizm@gmail.com'],  # Sadece bu adrese gönder
                    html_message=admin_html,
                    fail_silently=False,
                )
                
                messages.success(request, 'Rezervasyonunuz başarıyla alındı. Onay emaili gönderildi.')
                
            except Exception as email_error:
                print(f"Email gönderme hatası: {str(email_error)}")
                print(f"Detaylı hata: {traceback.format_exc()}")
                messages.warning(request, 'Rezervasyonunuz alındı ancak onay emaili gönderilemedi. En kısa sürede sizinle iletişime geçeceğiz.')
                
        except Exception as db_error:
            print(f"Veritabanı hatası: {str(db_error)}")
            print(f"Detaylı hata: {traceback.format_exc()}")
            messages.error(request, 'Rezervasyon sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.')
            
        return redirect('main:tour_detail', slug=slug)
    
    return redirect('main:tour_detail', slug=slug)

def about(request):
    """Hakkımızda sayfası."""
    return render(request, 'main/about.html')

def contact(request):
    """İletişim sayfasını görüntüler."""
    return render(request, 'main/contact.html')

@require_POST
def contact_form_submit(request):
    """İletişim formunu işleyip e-posta gönderir."""
    logger = logging.getLogger('main')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        context = {
            'name': name,
            'email': email,
            'phone': phone,
            'message': message,
            'datetime': timezone.now().strftime('%d-%m-%Y %H:%M')
        }
        
        try:
            # Yönetici bildirimi e-postası
            subject = 'Yeni İletişim Formu: ' + name
            to_email = 'mirzadeturizm@gmail.com'
            
            logger.info(f"Yönetici e-postası gönderiliyor. Konu: {subject}, Alıcı: {to_email}")
            
            admin_html_message = render_to_string('main/email/contact_email.html', context)
            admin_plain_message = strip_tags(admin_html_message)
            
            admin_email = EmailMultiAlternatives(
                subject,
                admin_plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email]
            )
            admin_email.attach_alternative(admin_html_message, "text/html")
            admin_result = admin_email.send()
            logger.info(f"Yönetici e-postası gönderildi. Sonuç: {admin_result}")
            
            # Kullanıcı onay e-postası
            subject = 'Mirzade Turizm - İletişim Formunuz Alındı'
            logger.info(f"Kullanıcı onay e-postası gönderiliyor. Alıcı: {email}")
            
            user_html_message = render_to_string('main/email/contact_confirmation.html', context)
            user_plain_message = strip_tags(user_html_message)
            
            user_email = EmailMultiAlternatives(
                subject,
                user_plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            user_email.attach_alternative(user_html_message, "text/html")
            user_result = user_email.send()
            logger.info(f"Kullanıcı onay e-postası gönderildi. Sonuç: {user_result}")
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            # E-posta yapılandırma detaylarını logla
            email_config = {
                'host': settings.EMAIL_HOST,
                'port': settings.EMAIL_PORT,
                'use_tls': settings.EMAIL_USE_TLS,
                'user': settings.EMAIL_HOST_USER,
                # Güvenlik için şifre loglanmıyor
            }
            
            logger.error(f"E-posta gönderimi sırasında hata: {error_msg}")
            logger.error(f"Hata detayları: {error_traceback}")
            logger.error(f"E-posta yapılandırması: {email_config}")
            
            return JsonResponse({'status': 'error', 'message': 'E-posta gönderilirken bir hata oluştu.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'})

def privacy_policy(request):
    """Gizlilik Politikası sayfası."""
    return render(request, 'main/privacy_policy.html')

def terms_of_use(request):
    """Kullanım Koşulları sayfası."""
    return render(request, 'main/terms_of_use.html')

def kvkk(request):
    """KVKK sayfası."""
    return render(request, 'main/kvkk.html')

def sss(request):
    """Sıkça Sorulan Sorular sayfası."""
    return render(request, 'main/sss.html')

def hotel_list(request):
    """Otellerin listelendiği sayfa"""
    hotels = Hotel.objects.filter(is_active=True)
    categories = HotelCategory.objects.all()
    amenities = HotelAmenity.objects.all()
    
    # Temel filtreleme işlemleri
    category_id = request.GET.get('category')
    if category_id:
        hotels = hotels.filter(category_id=category_id)
    
    star_rating = request.GET.get('star')
    if star_rating:
        hotels = hotels.filter(star_rating=star_rating)
    
    city = request.GET.get('city')
    if city:
        hotels = hotels.filter(city__icontains=city)
    
    country = request.GET.get('country')
    if country:
        hotels = hotels.filter(country__icontains=country)
    
    # Fiyat aralığı filtresi
    min_price = request.GET.get('min_price')
    if min_price:
        hotels = hotels.filter(room_types__price_per_night__gte=min_price).distinct()
    
    max_price = request.GET.get('max_price')
    if max_price:
        hotels = hotels.filter(room_types__price_per_night__lte=max_price).distinct()
    
    # Oda kapasitesi filtresi
    capacity = request.GET.get('capacity')
    if capacity:
        hotels = hotels.filter(room_types__capacity__gte=capacity).distinct()
    
    # Harem'e uzaklık filtresi
    distance_to_haram = request.GET.get('distance_to_haram')
    if distance_to_haram:
        hotels = hotels.filter(distance_to_haram__lte=distance_to_haram)
    
    # Özellik filtreleri
    amenity_ids = request.GET.getlist('amenities')
    if amenity_ids:
        for amenity_id in amenity_ids:
            hotels = hotels.filter(amenities__id=amenity_id)
    
    # İbadet özellikleri filtreleri
    if request.GET.get('has_prayer_room'):
        hotels = hotels.filter(has_prayer_room=True)
    
    if request.GET.get('has_quran'):
        hotels = hotels.filter(has_quran=True)
    
    if request.GET.get('has_qibla_direction'):
        hotels = hotels.filter(has_qibla_direction=True)
    
    if request.GET.get('has_prayer_mat'):
        hotels = hotels.filter(has_prayer_mat=True)
    
    # Konum özellikleri filtreleri
    if request.GET.get('view_of_kaaba'):
        hotels = hotels.filter(view_of_kaaba=True)
    
    if request.GET.get('view_of_haram'):
        hotels = hotels.filter(view_of_haram=True)
    
    # Ulaşım filtreleri
    if request.GET.get('has_haram_shuttle'):
        hotels = hotels.filter(has_haram_shuttle=True)
    
    if request.GET.get('has_airport_shuttle'):
        hotels = hotels.filter(has_airport_shuttle=True)
    
    if request.GET.get('has_mina_shuttle'):
        hotels = hotels.filter(has_mina_shuttle=True)
    
    if request.GET.get('has_arafat_shuttle'):
        hotels = hotels.filter(has_arafat_shuttle=True)
    
    # Yemek filtreleri
    if request.GET.get('has_breakfast'):
        hotels = hotels.filter(has_breakfast=True)
    
    if request.GET.get('has_lunch'):
        hotels = hotels.filter(has_lunch=True)
    
    if request.GET.get('has_dinner'):
        hotels = hotels.filter(has_dinner=True)
    
    if request.GET.get('has_turkish_food'):
        hotels = hotels.filter(has_turkish_food=True)
    
    # Hac dönemi özellikleri
    if request.GET.get('suitable_for_hajj'):
        hotels = hotels.filter(suitable_for_hajj=True)
    
    if request.GET.get('has_mina_tent'):
        hotels = hotels.filter(has_mina_tent=True)
    
    if request.GET.get('has_arafat_tent'):
        hotels = hotels.filter(has_arafat_tent=True)
    
    # Rehberlik hizmetleri
    if request.GET.get('has_turkish_guide'):
        hotels = hotels.filter(has_turkish_guide=True)
    
    if request.GET.get('has_religious_guide'):
        hotels = hotels.filter(has_religious_guide=True)
    
    if request.GET.get('has_24h_assistance'):
        hotels = hotels.filter(has_24h_assistance=True)
    
    # Ek hizmetler
    if request.GET.get('has_zamzam'):
        hotels = hotels.filter(has_zamzam=True)
    
    if request.GET.get('has_ihram'):
        hotels = hotels.filter(has_ihram=True)
    
    if request.GET.get('has_laundry'):
        hotels = hotels.filter(has_laundry=True)
    
    if request.GET.get('is_accessible'):
        hotels = hotels.filter(is_accessible=True)
    
    if request.GET.get('has_all_inclusive'):
        hotels = hotels.filter(has_all_inclusive=True)
    
    # Sıralama
    sort = request.GET.get('sort')
    if sort:
        if sort == 'distance_to_haram':
            hotels = hotels.order_by('distance_to_haram')
        elif sort == 'price_low':
            hotels = hotels.annotate(min_price=Min('room_types__price_per_night')).order_by('min_price')
        elif sort == 'price_high':
            hotels = hotels.annotate(min_price=Min('room_types__price_per_night')).order_by('-min_price')
        else:
            hotels = hotels.order_by(sort)
    
    context = {
        'hotels': hotels,
        'categories': categories,
        'amenities': amenities,
    }
    return render(request, 'main/hotel_list.html', context)

def hotel_detail(request, slug):
    """Otel detay sayfası."""
    hotel = get_object_or_404(Hotel, slug=slug)
    return render(request, 'main/hotel_detail.html', {'hotel': hotel})

def test_page(request):
    """Test sayfası."""
    return render(request, 'main/test.html')

# Blog View Fonksiyonları
def blog_home(request):
    """Blog ana sayfası"""
    posts = BlogPost.objects.filter(is_published=True).order_by('-published_date')
    categories = BlogCategory.objects.all()
    tags = BlogTag.objects.all()

    # Arşiv yıllarını al
    archive_years = BlogPost.objects.filter(
        is_published=True
    ).annotate(
        year=ExtractYear('published_date')
    ).values('year').annotate(
        count=Count('id')
    ).order_by('-year')

    print(f"Blog yazıları: {posts.count()} adet")
    
    # Kategori sayılarını hesapla
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_published=True).count()
    
    # Etiket sayılarını hesapla
    for tag in tags:
        tag.post_count = tag.posts.filter(is_published=True).count()
    
    # Popüler yazıları al
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:5]
    
    return render(request, 'main/blog/blog_home.html', {
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts,
        'archive_years': archive_years,
    })

def blog_detail(request, slug):
    """Blog yazı detayı"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Görüntülenme sayısını artır
    post.view_count += 1
    post.save()
    
    # Benzer yazılar
    similar_posts = BlogPost.objects.filter(
        category=post.category, 
        is_published=True
    ).exclude(id=post.id).order_by('-published_date')[:3]
    
    # Yorumlar
    comments = post.comments.filter(is_approved=True).order_by('-created_date')
    comment_count = comments.count()
    
    # Kategoriler
    categories = BlogCategory.objects.all()
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_published=True).count()
    
    # Etiketler
    tags = BlogTag.objects.all()
    for tag in tags:
        tag.post_count = tag.posts.filter(is_published=True).count()
    
    # Yorum formu
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        
        if name and email and content:
            BlogComment.objects.create(
                post=post,
                name=name,
                email=email,
                content=content
            )
            messages.success(request, 'Yorumunuz başarıyla gönderildi. Onaylandıktan sonra yayınlanacaktır.')
            return redirect('main:blog_detail', slug=slug)
    
    return render(request, 'main/blog/blog_detail.html', {
        'post': post,
        'similar_posts': similar_posts,
        'comments': comments,
        'comment_count': comment_count,
        'categories': categories,
        'tags': tags
    })

def blog_category(request, slug):
    """Blog kategori sayfası"""
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.filter(category=category, is_published=True).order_by('-published_date')
    
    # Kategoriler
    categories = BlogCategory.objects.all()
    for cat in categories:
        cat.post_count = BlogPost.objects.filter(category=cat, is_published=True).count()
    
    # Etiketler
    tags = BlogTag.objects.all()
    for tag in tags:
        tag.post_count = tag.posts.filter(is_published=True).count()
    
    # Popüler yazılar
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:5]
    
    return render(request, 'main/blog/blog_category.html', {
        'category': category,
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts
    })

def blog_tag(request, slug):
    """Blog etiket sayfası"""
    tag = get_object_or_404(BlogTag, slug=slug)
    posts = BlogPost.objects.filter(tags=tag, is_published=True).order_by('-published_date')
    
    # Kategoriler
    categories = BlogCategory.objects.all()
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_published=True).count()
    
    # Etiketler
    tags = BlogTag.objects.all()
    for blog_tag in tags:
        blog_tag.post_count = blog_tag.posts.filter(is_published=True).count()
    
    # Popüler yazılar
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:5]
    
    return render(request, 'main/blog/blog_tag.html', {
        'tag': tag,
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts
    })

def blog_search(request):
    """Blog arama sayfası"""
    query = request.GET.get('q', '')
    
    if query:
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(summary__icontains=query),
            is_published=True
        ).order_by('-published_date')
    else:
        posts = BlogPost.objects.none()
    
    # Kategoriler
    categories = BlogCategory.objects.all()
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_published=True).count()
    
    # Etiketler
    tags = BlogTag.objects.all()
    for tag in tags:
        tag.post_count = tag.posts.filter(is_published=True).count()
    
    # Popüler yazılar
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:5]
    
    return render(request, 'main/blog/blog_search.html', {
        'query': query,
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts
    })

def documents(request):
    """Resmi belgeler sayfası."""
    return render(request, 'main/documents.html')

def luxury_umre(request):
    """Lüks Umre sayfası: Lüks ve VIP umre turları için özel sayfa."""
    # Lüks ve VIP umre turlarını filtrele
    luxury_tours = Tour.objects.filter(
        Q(category='umre') & 
        (Q(title__icontains='lüks') | Q(title__icontains='vip') | 
         Q(description__icontains='lüks') | Q(description__icontains='vip'))
    ).order_by('-date')
    
    # Photologue galerisini al
    try:
        # 'luxury-umre' slug'ına sahip galeriyi bul
        gallery = Gallery.objects.get(slug='luxury-umre')
    except Gallery.DoesNotExist:
        # Galeri bulunamazsa None olarak ayarla
        gallery = None
    
    return render(request, 'main/luxury.html', {
        'luxury_tours': luxury_tours,
        'page_title': 'Lüks Umre Turları',
        'page_description': 'Mirzade Turizm ile lüks ve VIP umre turları. Konforlu konaklama, özel rehberlik ve premium hizmetler.',
        'gallery': gallery
    })

def luxury_package(request):
    """Lüks Umre Paketi detay sayfası."""
    return render(request, 'main/luxury_package.html', {
        'page_title': 'Lüks Umre Paketi',
        'page_description': 'Harem\'e yakın 5 yıldızlı otellerde konaklama, özel rehberlik hizmetleri ve VIP transfer imkanları ile unutulmaz bir umre deneyimi.'
    })

def premium_package(request):
    """Premium Umre Paketi detay sayfası."""
    return render(request, 'main/premium_package.html', {
        'page_title': 'Premium Umre Paketi',
        'page_description': 'Özel grup imkanları, lüks konaklama ve zengin kültürel programlar ile dolu dolu bir umre deneyimi.'
    })

def vip_package(request):
    """VIP Umre Paketi detay sayfası."""
    return render(request, 'main/vip_package.html', {
        'page_title': 'VIP Umre Paketi',
        'page_description': 'En üst düzey hizmet anlayışı, özel asistanlık ve kişiye özel program ile ayrıcalıklı bir umre deneyimi.'
    })

def luxury_reservation(request):
    """Lüks Umre Rezervasyon sayfası"""
    # Sadece umre kategorisindeki turları filtrele
    luxury_tours = Tour.objects.filter(
        category='umre',  # Umre kategorisi
        is_active=True,  # Aktif turlar
        is_luxury=True  # Lüks turlar
    ).order_by('date')
    
    if request.method == 'POST':
        # Form verilerini al
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        participants = request.POST.get('participants')
        room_type = request.POST.get('room_type')
        notes = request.POST.get('notes')
        tour_id = request.POST.get('tour_id')
        
        if not tour_id:
            messages.error(request, 'Lütfen bir tur seçiniz.')
            return redirect('main:luxury_reservation')
        
        tour = get_object_or_404(Tour, id=tour_id)
        
        # Rezervasyon veritabanına kaydediliyor
        reservation = TourReservation.objects.create(
            tour=tour,
            name=name,
            email=email,
            phone=phone,
            participants=participants if participants else 1,
            room_type=room_type,
            notes=notes
        )
        
        # Müşteriye bilgilendirme e-postası gönder
        try:
            # Müşteri e-postası için HTML içeriği oluştur
            customer_html_message = render_to_string('main/email/reservation_confirmation.html', {
                'name': name,
                'tour': tour,
                'reservation': reservation,
            })
            customer_plain_message = strip_tags(customer_html_message)
            
            # Müşteriye e-posta gönder
            send_mail(
                subject=f'Mirzade TUR - {tour.title} Rezervasyon Onayı',
                message=customer_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=customer_html_message,
                fail_silently=False,
            )
            
            # Yöneticiye bildirim e-postası gönder
            admin_html_message = render_to_string('main/email/admin_notification.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'tour': tour,
                'room_type': room_type,
                'notes': notes,
                'reservation': reservation,
            })
            admin_plain_message = strip_tags(admin_html_message)
            
            # Yöneticiye e-posta gönder
            send_mail(
                subject=f'Yeni Lüks Umre Rezervasyonu: {tour.title}',
                message=admin_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['mirzadeturizm@gmail.com'],  # Sadece bu adrese gönder
                html_message=admin_html_message,
                fail_silently=False,
            )
            
            messages.success(request, 'Lüks umre rezervasyon talebiniz başarıyla alınmıştır. Onay e-postası gönderildi. VIP müşteri temsilcimiz en kısa sürede sizinle iletişime geçecektir.')
        except Exception as e:
            # E-posta gönderiminde hata olursa
            print(f"E-posta gönderme hatası: {e}")
            print(traceback.format_exc())
            messages.warning(request, 'Rezervasyon talebiniz alındı ancak e-posta gönderiminde bir sorun oluştu. En kısa sürede sizinle iletişime geçeceğiz.')
        
        return redirect('main:luxury')
    
    context = {
        'luxury_tours': luxury_tours,  # Template'de bu isimle kullanılıyor
        'page_title': 'Lüks Umre Rezervasyon',
        'page_description': 'Mirzade Turizm ile lüks ve VIP umre turları için özel rezervasyon sayfası.'
    }
    return render(request, 'main/luxury_reservation.html', context)

def blog_archive_year(request, year):
    """Yıllık blog arşivi"""
    posts = BlogPost.objects.filter(
        is_published=True,
        published_date__year=year
    ).order_by('-published_date')

    # Arşiv yıllarını al
    archive_years = BlogPost.objects.filter(
        is_published=True
    ).annotate(
        year=ExtractYear('published_date')
    ).values('year').annotate(
        count=Count('id')
    ).order_by('-year')

    # Kategorileri ve sayılarını al
    categories = BlogCategory.objects.all()
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_published=True).count()

    # Etiketleri al
    tags = BlogTag.objects.all()
    for tag in tags:
        tag.post_count = tag.posts.filter(is_published=True).count()

    # Popüler yazıları al
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:5]

    context = {
        'posts': posts,
        'year': year,
        'archive_years': archive_years,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts,
    }

    return render(request, 'main/blog/blog_archive.html', context)

def blog_archive_month(request, year, month):
    """Aylık blog arşivi"""
    posts = BlogPost.objects.filter(
        is_published=True,
        published_date__year=year,
        published_date__month=month
    ).order_by('-published_date')

    # Arşiv yıllarını ve aylarını al
    archive_months = BlogPost.objects.filter(
        is_published=True,
        published_date__year=year
    ).annotate(
        month=ExtractMonth('published_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')

    # Kategorileri ve sayılarını al
    categories = BlogCategory.objects.all()
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_published=True).count()

    # Etiketleri al
    tags = BlogTag.objects.all()
    for tag in tags:
        tag.post_count = tag.posts.filter(is_published=True).count()

    # Popüler yazıları al
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:5]

    # Ay adını al
    month_name = datetime(year, month, 1).strftime('%B')

    context = {
        'posts': posts,
        'year': year,
        'month': month,
        'month_name': month_name,
        'archive_months': archive_months,
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts,
    }

    return render(request, 'main/blog/blog_archive.html', context)

def blog_categories(request):
    """Blog kategorileri listesi sayfası"""
    categories = BlogCategory.objects.all()
    
    # Kategori sayılarını hesapla
    for category in categories:
        category.post_count = BlogPost.objects.filter(category=category, is_published=True).count()
    
    # Etiketler
    tags = BlogTag.objects.all()
    for tag in tags:
        tag.post_count = tag.posts.filter(is_published=True).count()
    
    # Popüler yazılar
    popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:5]
    
    return render(request, 'main/blog/blog_categories.html', {
        'categories': categories,
        'tags': tags,
        'popular_posts': popular_posts
    })

def health(request):
    """
    Sağlık kontrolü için endpoint.
    Veritabanı ve Redis bağlantılarını kontrol eder.
    """
    # Sistem durumu
    status = {
        "status": "up",
        "database": "up",
        "redis": "up",
        "message": "System is healthy"
    }
    
    # Veritabanı kontrolü
    try:
        db_conn = connections['default']
        db_conn.cursor()
    except OperationalError:
        status["status"] = "degraded"
        status["database"] = "down"
        status["message"] = "Database connection failed"
    
    # Redis kontrolü
    try:
        redis_host = os.environ.get('REDIS_HOST', 'redis')
        redis_port = os.environ.get('REDIS_PORT', 6379)
        r = redis.Redis(host=redis_host, port=redis_port, db=0)
        r.ping()
    except RedisError:
        if status["status"] == "up":
            status["status"] = "degraded"
        elif status["database"] == "down":
            status["status"] = "down"
        status["redis"] = "down"
        status["message"] = f"{status['message']}. Redis connection failed"
    
    # Docker'a özel health check için basit OK yanıtı
    if request.GET.get('format') == 'simple':
        if status["status"] == "up":
            return HttpResponse("OK", content_type="text/plain")
        else:
            return HttpResponse("ERROR", content_type="text/plain", status=500)
    
    # Varsayılan JSON yanıtı
    return JsonResponse(status)
