from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Tour, Slider, TourTransportation, TourActivity, 
    TourProgram, TourReview, TourFAQ, TourGallery, TourReservation,
    Category, HotelCategory, HotelAmenity, Hotel, HotelImage, RoomType, TourHotel,
    BlogCategory, BlogTag, BlogPost, BlogComment, SiteSettings
)
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from .admin_dashboard import get_admin_dashboard_html
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Admin site özelleştirme
class CustomAdminSite(AdminSite):
    site_header = 'Mirzade Turizm Yönetim Paneli'
    site_title = 'Mirzade Turizm Admin'
    index_title = 'Yönetim Paneli'
    site_url = '/'
    
    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = '/static/css/admin.css'
        return context
    
    def index(self, request, extra_context=None):
        """Özelleştirilmiş admin paneli anasayfası"""
        app_list = self.get_app_list(request)
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            'dashboard_html': get_admin_dashboard_html(),
            **(extra_context or {}),
        }
        
        request.current_app = self.name
        
        return TemplateResponse(request, 'admin/index.html', context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Özel admin URL'leri buraya eklenebilir
        ]
        return custom_urls + urls

# SiteSettings için admin sınıfı
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Genel Ayarlar', {
            'fields': ('site_title', 'site_description', 'logo', 'favicon')
        }),
        ('İletişim Bilgileri', {
            'fields': ('email', 'phone', 'whatsapp', 'address')
        }),
        ('Sosyal Medya', {
            'fields': ('facebook', 'twitter', 'instagram', 'youtube', 'linkedin')
        }),
        ('SEO Ayarları', {
            'fields': ('meta_keywords', 'meta_description', 'google_analytics')
        }),
        ('Diğer Ayarlar', {
            'fields': ('footer_text', 'copyright_text')
        }),
    )
    
    def has_add_permission(self, request):
        # Sadece bir kayıt olmasını sağla
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Silme işlemini engelle
        return False

# Özelleştirilmiş admin sitesini oluştur
admin_site = CustomAdminSite(name='mirzade_admin')

# Django'nun varsayılan User ve Group modellerini kaydet
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(SiteSettings, SiteSettingsAdmin)

class TourTransportationInline(admin.TabularInline):
    model = TourTransportation
    extra = 1

class TourProgramInline(admin.StackedInline):
    model = TourProgram
    extra = 1
    filter_horizontal = ('activities',)

class TourGalleryInline(admin.TabularInline):
    model = TourGallery
    extra = 3

class TourFAQInline(admin.TabularInline):
    model = TourFAQ
    extra = 3

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1

class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1

class TourHotelInline(admin.TabularInline):
    model = TourHotel
    extra = 1
    autocomplete_fields = ['hotel', 'room_type']

class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    readonly_fields = ('name', 'email', 'created_date')
    can_delete = True
    fields = ('name', 'email', 'content', 'created_date', 'is_approved')

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'price', 'is_active', 'is_luxury')
    list_filter = ('category', 'is_active', 'is_luxury')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TourTransportationInline, TourProgramInline, TourGalleryInline, TourFAQInline, TourHotelInline]
    actions = ['copy_tour']
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'description', 'category', 'is_active')
        }),
        ('Fiyat ve Tarih', {
            'fields': ('price', 'currency', 'date', 'duration')
        }),
        ('Lüks Tur Özellikleri', {
            'fields': ('is_luxury', 'luxury_features', 'luxury_amenities', 'vip_transfer', 'special_guide'),
            'classes': ('collapse',)
        }),
        ('Oda Fiyatlandırması', {
            'fields': ('double_room_price', 'triple_room_price', 'quad_room_price'),
            'classes': ('collapse',)
        }),
        ('Görsel ve Konum', {
            'fields': ('image', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
    )
    
    def copy_tour_button(self, obj):
        """Tur kopyalama butonu oluşturur"""
        url = reverse('admin:copy_tour', args=[obj.pk])
        return format_html('<a class="button" href="{}">Kopyala</a>', url)
    copy_tour_button.short_description = 'Kopyala'
    
    def copy_tour(self, request, queryset):
        """Seçilen turları kopyalar"""
        for tour in queryset:
            self._copy_tour(tour)
        
        self.message_user(request, f"{len(queryset)} tur başarıyla kopyalandı.", messages.SUCCESS)
    copy_tour.short_description = "Seçili turları kopyala"
    
    def _copy_tour(self, tour):
        """Bir turu kopyalar ve ilişkili tüm verileri de kopyalar"""
        # Orijinal turun ID'sini saklayalım
        original_tour_id = tour.id
        
        # Orijinal tur resmini saklayalım
        original_image = None
        if tour.image:
            original_image = tour.image
        
        # Tur nesnesini kopyala
        tour.pk = None
        tour.title = f"{tour.title} (Kopya)"
        tour.date = timezone.now().date()  # Bugünün tarihini ata
        tour.is_active = False  # Varsayılan olarak pasif yap
        tour.save()
        
        # Eğer orijinal resim varsa, kopyalayalım
        if original_image:
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage
            import os
            
            # Orijinal dosya adını al
            file_name = os.path.basename(original_image.name)
            # Yeni bir dosya adı oluştur
            name_parts = os.path.splitext(file_name)
            new_file_name = f"{name_parts[0]}_copy{name_parts[1]}"
            
            # Resmi kopyala
            tour.image.save(
                new_file_name,
                ContentFile(original_image.read()),
                save=True
            )
        
        # Yeni tur ID'sini alalım
        new_tour_id = tour.id
        
        # Ulaşım bilgilerini kopyala
        for transport in TourTransportation.objects.filter(tour_id=original_tour_id):
            transport.pk = None
            transport.tour = tour
            transport.save()
        
        # Tur programını kopyala
        for program in TourProgram.objects.filter(tour_id=original_tour_id):
            old_activities = list(program.activities.all())
            program.pk = None
            program.tour = tour
            program.save()
            
            # Aktiviteleri ekle
            for activity in old_activities:
                program.activities.add(activity)
        
        # Galeri resimlerini kopyala
        for gallery in TourGallery.objects.filter(tour_id=original_tour_id):
            # Orijinal resmi sakla
            original_gallery_image = None
            if gallery.image:
                original_gallery_image = gallery.image
                
            gallery.pk = None
            gallery.tour = tour
            gallery.save()
            
            # Eğer orijinal galeri resmi varsa, kopyalayalım
            if original_gallery_image:
                from django.core.files.base import ContentFile
                import os
                
                # Orijinal dosya adını al
                file_name = os.path.basename(original_gallery_image.name)
                # Yeni bir dosya adı oluştur
                name_parts = os.path.splitext(file_name)
                new_file_name = f"{name_parts[0]}_copy{name_parts[1]}"
                
                # Resmi kopyala
                gallery.image.save(
                    new_file_name,
                    ContentFile(original_gallery_image.read()),
                    save=True
                )
        
        # SSS'leri kopyala
        for faq in TourFAQ.objects.filter(tour_id=original_tour_id):
            faq.pk = None
            faq.tour = tour
            faq.save()
        
        return tour
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('copy/<int:tour_id>/', self.admin_site.admin_view(self.copy_tour_view), name='copy_tour'),
        ]
        return custom_urls + urls
    
    def copy_tour_view(self, request, tour_id):
        """Tek bir turu kopyalamak için view"""
        tour = Tour.objects.get(pk=tour_id)
        new_tour = self._copy_tour(tour)
        
        self.message_user(request, f"'{tour.title}' başarıyla kopyalandı.", messages.SUCCESS)
        return HttpResponseRedirect(reverse('admin:main_tour_change', args=[new_tour.pk]))

@admin.register(TourActivity)
class TourActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration')
    search_fields = ('name',)

@admin.register(TourProgram)
class TourProgramAdmin(admin.ModelAdmin):
    list_display = ('tour', 'day', 'title', 'accommodation', 'meals')
    list_filter = ('tour', 'day')
    search_fields = ('title', 'description')
    filter_horizontal = ('activities',)
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('tour', 'day', 'title', 'description')
        }),
        ('Aktiviteler', {
            'fields': ('activities',)
        }),
        ('Konaklama ve Yemek', {
            'fields': ('accommodation', 'meals')
        }),
        ('Zaman ve Konum', {
            'fields': ('start_time', 'end_time', 'location')
        }),
        ('Ek Bilgiler', {
            'fields': ('important_notes',)
        }),
    )

@admin.register(TourReview)
class TourReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'tour', 'rating', 'created_at', 'is_approved')
    list_filter = ('tour', 'rating', 'is_approved')
    search_fields = ('name', 'comment')
    list_editable = ('is_approved',)

@admin.register(TourReservation)
class TourReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'tour', 'email', 'phone', 'room_type', 'participants', 'created_at', 'colored_status')
    list_filter = ('tour', 'status', 'room_type', 'created_at')
    search_fields = ('name', 'email', 'phone', 'notes')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    actions = ['mark_as_confirmed', 'mark_as_cancelled', 'mark_as_pending']
    
    fieldsets = (
        ('Müşteri Bilgileri', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Rezervasyon Detayları', {
            'fields': ('tour', 'participants', 'room_type', 'status', 'created_at')
        }),
        ('Ek Bilgiler', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        # En yeni rezervasyonları üstte göster
        return super().get_queryset(request).order_by('-created_at')
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} rezervasyon onaylandı.')
    mark_as_confirmed.short_description = "Seçili rezervasyonları onayla"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} rezervasyon iptal edildi.')
    mark_as_cancelled.short_description = "Seçili rezervasyonları iptal et"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} rezervasyon beklemeye alındı.')
    mark_as_pending.short_description = "Seçili rezervasyonları beklemeye al"

    def colored_status(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
        }
        status_display = {
            'pending': 'Beklemede',
            'confirmed': 'Onaylandı',
            'cancelled': 'İptal Edildi',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            status_display.get(obj.status, obj.status)
        )
    colored_status.short_description = 'Durum'
    colored_status.admin_order_field = 'status'

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'star_rating', 'category', 'is_active')
    list_filter = ('star_rating', 'city', 'country', 'category', 'is_active', 
                  'has_prayer_room', 'has_haram_shuttle', 'suitable_for_hajj')
    search_fields = ('name', 'description', 'address', 'city', 'country')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [HotelImageInline, RoomTypeInline]
    filter_horizontal = ('amenities',)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'description', 'address', 'city', 'country', 'star_rating', 'category', 'amenities', 'is_active')
        }),
        ('Konum Bilgileri', {
            'fields': ('latitude', 'longitude')
        }),
        ('Hac ve Umre Özellikleri', {
            'fields': ('distance_to_haram', 'view_of_kaaba', 'view_of_haram', 'has_prayer_room', 'has_quran', 'has_qibla_direction', 'has_prayer_mat')
        }),
        ('Ulaşım Özellikleri', {
            'fields': ('has_haram_shuttle', 'has_airport_shuttle', 'has_mina_shuttle', 'has_arafat_shuttle')
        }),
        ('Yemek Özellikleri', {
            'fields': ('has_breakfast', 'has_lunch', 'has_dinner', 'has_turkish_food')
        }),
        ('Hac Dönemi Özellikleri', {
            'fields': ('suitable_for_hajj', 'has_mina_tent', 'has_arafat_tent')
        }),
        ('Rehberlik Hizmetleri', {
            'fields': ('has_turkish_guide', 'has_religious_guide', 'has_24h_assistance')
        }),
        ('Ek Hizmetler', {
            'fields': ('has_zamzam', 'has_ihram', 'has_laundry', 'is_accessible', 'has_all_inclusive')
        }),
    )

@admin.register(HotelCategory)
class HotelCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']

@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'title', 'is_main', 'order']
    list_filter = ['is_main', 'hotel']
    search_fields = ['hotel__name', 'title']

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'name', 'capacity', 'price_per_night']
    list_filter = ['hotel', 'capacity']
    search_fields = ['hotel__name', 'name']

@admin.register(TourHotel)
class TourHotelAdmin(admin.ModelAdmin):
    list_display = ['tour', 'hotel', 'nights', 'room_type', 'is_default']
    list_filter = ['is_default', 'hotel', 'tour']
    search_fields = ['tour__title', 'hotel__name']

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Yazı Sayısı'

@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Yazı Sayısı'

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_date', 'is_published', 'view_count')
    list_filter = ('category', 'tags', 'is_published', 'published_date')
    search_fields = ('title', 'content', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_date'
    inlines = [BlogCommentInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'is_published')
        }),
        ('İçerik', {
            'fields': ('content', 'summary', 'image')
        }),
        ('İstatistikler', {
            'fields': ('view_count', 'published_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('published_date', 'updated_date', 'view_count')
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css',)
        }
        js = ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/js/all.min.js',)

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'created_date', 'is_approved')
    list_filter = ('is_approved', 'created_date')
    search_fields = ('name', 'email', 'content')
    list_editable = ('is_approved',)
    date_hierarchy = 'created_date'
    
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} yorum onaylandı.")
    approve_comments.short_description = "Seçili yorumları onayla"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} yorumun onayı kaldırıldı.")
    disapprove_comments.short_description = "Seçili yorumların onayını kaldır"

class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')

# Admin panelini özelleştirmek için CSS ekleyelim
class AdminStyleMixin:
    class Media:
        css = {
            'all': ('css/admin/custom_admin.css',)
        }
        js = ('js/admin/custom_admin.js',)

admin.site.site_header = "Mirzade Turizm Yönetim Paneli"
admin.site.site_title = "Mirzade Turizm"
admin.site.index_title = "Veri Yönetimi"

# Tüm modelleri özelleştirilmiş admin sitesine kaydet
admin_site.register(Tour, TourAdmin)
admin_site.register(Slider, SliderAdmin)
admin_site.register(TourActivity, TourActivityAdmin)
admin_site.register(TourProgram, TourProgramAdmin)
admin_site.register(TourReview, TourReviewAdmin)
admin_site.register(TourReservation, TourReservationAdmin)
admin_site.register(Hotel, HotelAdmin)
admin_site.register(HotelCategory, HotelCategoryAdmin)
admin_site.register(HotelAmenity, HotelAmenityAdmin)
admin_site.register(HotelImage, HotelImageAdmin)
admin_site.register(RoomType, RoomTypeAdmin)
admin_site.register(TourHotel, TourHotelAdmin)
admin_site.register(BlogCategory, BlogCategoryAdmin)
admin_site.register(BlogTag, BlogTagAdmin)
admin_site.register(BlogPost, BlogPostAdmin)
admin_site.register(BlogComment, BlogCommentAdmin)
admin_site.register(Category)