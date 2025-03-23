from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import home, category_filter, tour_detail, search_tours, tour_reservation, about, contact, contact_form_submit, privacy_policy, terms_of_use, kvkk, sss, hotel_list, hotel_detail, test_page, blog_home, blog_detail, blog_category, blog_tag, blog_search, documents, luxury_umre, luxury_reservation, luxury_package, premium_package, vip_package, blog_archive_year, blog_archive_month, blog_categories, health

app_name = 'main'  # Namespace tanımı

urlpatterns = [
    path('', home, name='home'),
    path('category/<str:category>/', category_filter, name='category_filter'),  # Kategori filtreleme URL'si
    path('tur/<slug:slug>/', tour_detail, name='tour_detail'),  # Tur detay sayfası URL'si
    path('search/', search_tours, name='search_tours'),  # Tur arama URL'si
    path('tour/<slug:slug>/reservation/', tour_reservation, name='tour_reservation'),  # Tur rezervasyon URL'si
    path('about/', about, name='about'),  # Hakkımızda sayfası URL'si
    path('contact/', contact, name='contact'),  # İletişim sayfası URL'si
    path('contact/submit/', contact_form_submit, name='contact_form_submit'),  # İletişim formu gönderim API'si
    path('privacy-policy/', privacy_policy, name='privacy_policy'),  # Gizlilik Politikası URL'si
    path('terms-of-use/', terms_of_use, name='terms_of_use'),  # Kullanım Koşulları URL'si
    path('kvkk/', kvkk, name='kvkk'),  # KVKK URL'si
    path('sss/', sss, name='sss'),  # Sıkça Sorulan Sorular URL'si
    path('hotels/', hotel_list, name='hotel_list'),
    path('hotels/<slug:slug>/', hotel_detail, name='hotel_detail'),
    path('documents/', documents, name='documents'),  # Belgelerimiz sayfası URL'si
    path('luxury/', luxury_umre, name='luxury'),  # Lüks umre sayfası URL'si
    path('luxury/package/', luxury_package, name='luxury_package'),  # Lüks umre paketi detay sayfası URL'si
    path('luxury/premium/', premium_package, name='premium_package'),  # Premium umre paketi detay sayfası URL'si
    path('luxury/vip/', vip_package, name='vip_package'),  # VIP umre paketi detay sayfası URL'si
    path('luxury/reservation/', luxury_reservation, name='luxury_reservation'),  # Lüks umre rezervasyon sayfası URL'si
    path('test/', test_page, name='test_page'),  # Test sayfası URL'si
    
    # Blog URL'leri
    path('blog/', blog_home, name='blog_home'),
    path('blog/search/', blog_search, name='blog_search'),
    path('blog/categories/', blog_categories, name='blog_categories'),
    path('blog/category/<slug:slug>/', blog_category, name='blog_category'),
    path('blog/tag/<slug:slug>/', blog_tag, name='blog_tag'),
    path('blog/archive/<int:year>/', blog_archive_year, name='blog_archive_year'),
    path('blog/archive/<int:year>/<int:month>/', blog_archive_month, name='blog_archive_month'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
    
    # Sağlık kontrolü endpointi
    path('health/', health, name='health'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)