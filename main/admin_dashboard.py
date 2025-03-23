from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from django.db.models import Count, Sum
from .models import Tour, TourReservation, BlogPost, Hotel

class DashboardStats:
    """Admin paneli için istatistik sağlayan sınıf"""
    
    @staticmethod
    def get_tour_stats():
        """Tur istatistiklerini döndürür"""
        total_tours = Tour.objects.count()
        active_tours = Tour.objects.filter(is_active=True).count()
        
        return {
            'total': total_tours,
            'active': active_tours,
            'inactive': total_tours - active_tours,
        }
    
    @staticmethod
    def get_reservation_stats():
        """Rezervasyon istatistiklerini döndürür"""
        total_reservations = TourReservation.objects.count()
        confirmed_reservations = TourReservation.objects.filter(status='CONFIRMED').count()
        pending_reservations = TourReservation.objects.filter(status='PENDING').count()
        cancelled_reservations = TourReservation.objects.filter(status='CANCELLED').count()
        
        return {
            'total': total_reservations,
            'confirmed': confirmed_reservations,
            'pending': pending_reservations,
            'cancelled': cancelled_reservations,
        }
    
    @staticmethod
    def get_blog_stats():
        """Blog istatistiklerini döndürür"""
        total_posts = BlogPost.objects.count()
        published_posts = BlogPost.objects.filter(is_published=True).count()
        draft_posts = total_posts - published_posts
        total_views = BlogPost.objects.aggregate(total_views=Sum('view_count'))['total_views'] or 0
        
        return {
            'total': total_posts,
            'published': published_posts,
            'draft': draft_posts,
            'total_views': total_views,
        }
    
    @staticmethod
    def get_hotel_stats():
        """Otel istatistiklerini döndürür"""
        total_hotels = Hotel.objects.count()
        active_hotels = Hotel.objects.filter(is_active=True).count()
        
        return {
            'total': total_hotels,
            'active': active_hotels,
            'inactive': total_hotels - active_hotels,
        }
    
    @staticmethod
    def get_all_stats():
        """Tüm istatistikleri döndürür"""
        return {
            'tours': DashboardStats.get_tour_stats(),
            'reservations': DashboardStats.get_reservation_stats(),
            'blog': DashboardStats.get_blog_stats(),
            'hotels': DashboardStats.get_hotel_stats(),
        }

def get_admin_dashboard_html():
    """Admin paneli için dashboard HTML'ini döndürür"""
    stats = DashboardStats.get_all_stats()
    
    # URL'leri hazırla - try/except bloğu ile hataları yakalayalım
    try:
        # Özelleştirilmiş admin sitesi için URL'leri oluştur
        tour_url = "#"
        reservation_url = "#"
        blog_url = "#"
        hotel_url = "#"
        add_tour_url = "#"
        add_blog_url = "#"
        add_hotel_url = "#"
        pending_reservations_url = "#"
    except Exception as e:
        # Hata durumunda # ile başlayan URL'ler kullan
        tour_url = "#"
        reservation_url = "#"
        blog_url = "#"
        hotel_url = "#"
        add_tour_url = "#"
        add_blog_url = "#"
        add_hotel_url = "#"
        pending_reservations_url = "#"
    
    # HTML içeriğini oluştur
    html = f"""
    <div class="dashboard-container">
        <div class="dashboard-welcome">
            <div class="welcome-icon">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="welcome-content">
                <h2>Mirzade Turizm Yönetim Paneli</h2>
                <p>Hoş geldiniz! Aşağıda sistemdeki güncel istatistikleri görebilirsiniz.</p>
            </div>
        </div>
        
        <div class="dashboard-stats">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-plane"></i>
                    </div>
                    <h3>Turlar</h3>
                </div>
                <div class="stat-body">
                    <div class="stat-numbers">
                        <div class="stat-number">
                            <span class="number">{stats['tours']['total']}</span>
                            <span class="label">Toplam</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['tours']['active']}</span>
                            <span class="label">Aktif</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['tours']['inactive']}</span>
                            <span class="label">Pasif</span>
                        </div>
                    </div>
                </div>
                <div class="stat-footer">
                    <a href="{tour_url}" class="stat-link">
                        <i class="fas fa-list"></i> Turları Yönet
                    </a>
                    <a href="{add_tour_url}" class="stat-link">
                        <i class="fas fa-plus"></i> Yeni Tur Ekle
                    </a>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-calendar-check"></i>
                    </div>
                    <h3>Rezervasyonlar</h3>
                </div>
                <div class="stat-body">
                    <div class="stat-numbers">
                        <div class="stat-number">
                            <span class="number">{stats['reservations']['total']}</span>
                            <span class="label">Toplam</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['reservations']['confirmed']}</span>
                            <span class="label">Onaylı</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['reservations']['pending']}</span>
                            <span class="label">Bekleyen</span>
                        </div>
                    </div>
                </div>
                <div class="stat-footer">
                    <a href="{reservation_url}" class="stat-link">
                        <i class="fas fa-list"></i> Rezervasyonları Yönet
                    </a>
                    <a href="{pending_reservations_url}" class="stat-link">
                        <i class="fas fa-clock"></i> Bekleyen Rezervasyonlar
                    </a>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-newspaper"></i>
                    </div>
                    <h3>Blog</h3>
                </div>
                <div class="stat-body">
                    <div class="stat-numbers">
                        <div class="stat-number">
                            <span class="number">{stats['blog']['total']}</span>
                            <span class="label">Toplam</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['blog']['published']}</span>
                            <span class="label">Yayında</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['blog']['total_views']}</span>
                            <span class="label">Görüntülenme</span>
                        </div>
                    </div>
                </div>
                <div class="stat-footer">
                    <a href="{blog_url}" class="stat-link">
                        <i class="fas fa-list"></i> Blog Yazılarını Yönet
                    </a>
                    <a href="{add_blog_url}" class="stat-link">
                        <i class="fas fa-plus"></i> Yeni Blog Yazısı
                    </a>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">
                        <i class="fas fa-hotel"></i>
                    </div>
                    <h3>Oteller</h3>
                </div>
                <div class="stat-body">
                    <div class="stat-numbers">
                        <div class="stat-number">
                            <span class="number">{stats['hotels']['total']}</span>
                            <span class="label">Toplam</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['hotels']['active']}</span>
                            <span class="label">Aktif</span>
                        </div>
                        <div class="stat-number">
                            <span class="number">{stats['hotels']['inactive']}</span>
                            <span class="label">Pasif</span>
                        </div>
                    </div>
                </div>
                <div class="stat-footer">
                    <a href="{hotel_url}" class="stat-link">
                        <i class="fas fa-list"></i> Otelleri Yönet
                    </a>
                    <a href="{add_hotel_url}" class="stat-link">
                        <i class="fas fa-plus"></i> Yeni Otel Ekle
                    </a>
                </div>
            </div>
        </div>
        
        <div class="dashboard-quick-actions">
            <h3><i class="fas fa-bolt"></i> Hızlı İşlemler</h3>
            <div class="quick-actions-grid">
                <a href="{add_tour_url}" class="quick-action-card">
                    <div class="quick-action-icon">
                        <i class="fas fa-plane-departure"></i>
                    </div>
                    <div class="quick-action-text">
                        <h4>Yeni Tur Ekle</h4>
                        <p>Sisteme yeni bir tur ekleyin</p>
                    </div>
                </a>
                <a href="{add_blog_url}" class="quick-action-card">
                    <div class="quick-action-icon">
                        <i class="fas fa-pen-fancy"></i>
                    </div>
                    <div class="quick-action-text">
                        <h4>Yeni Blog Yazısı</h4>
                        <p>Blog'a yeni bir yazı ekleyin</p>
                    </div>
                </a>
                <a href="{add_hotel_url}" class="quick-action-card">
                    <div class="quick-action-icon">
                        <i class="fas fa-building"></i>
                    </div>
                    <div class="quick-action-text">
                        <h4>Yeni Otel Ekle</h4>
                        <p>Sisteme yeni bir otel ekleyin</p>
                    </div>
                </a>
                <a href="{pending_reservations_url}" class="quick-action-card">
                    <div class="quick-action-icon">
                        <i class="fas fa-clipboard-check"></i>
                    </div>
                    <div class="quick-action-text">
                        <h4>Bekleyen Rezervasyonlar</h4>
                        <p>Onay bekleyen rezervasyonları görüntüleyin</p>
                    </div>
                </a>
            </div>
        </div>
    </div>
    
    <style>
        .dashboard-container {{
            padding: 0;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .dashboard-welcome {{
            background: linear-gradient(135deg, #00927E 0%, #007A68 100%);
            color: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .welcome-icon {{
            font-size: 40px;
            margin-right: 20px;
            background: rgba(255,255,255,0.2);
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .welcome-content h2 {{
            margin: 0 0 10px 0;
            font-size: 24px;
            font-weight: 600;
        }}
        
        .welcome-content p {{
            margin: 0;
            opacity: 0.9;
            font-size: 16px;
        }}
        
        .dashboard-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            overflow: hidden;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .stat-header {{
            padding: 20px;
            background: #f9f7f2;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #eee;
        }}
        
        .stat-icon {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #00927E 0%, #007A68 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            color: white;
            font-size: 20px;
        }}
        
        .stat-header h3 {{
            margin: 0;
            color: #333;
            font-size: 18px;
            font-weight: 600;
        }}
        
        .stat-body {{
            padding: 20px;
            flex-grow: 1;
        }}
        
        .stat-numbers {{
            display: flex;
            justify-content: space-between;
        }}
        
        .stat-number {{
            text-align: center;
            flex: 1;
        }}
        
        .stat-number .number {{
            display: block;
            font-size: 28px;
            font-weight: bold;
            color: #00927E;
            margin-bottom: 5px;
        }}
        
        .stat-number .label {{
            display: block;
            font-size: 13px;
            color: #666;
            font-weight: 500;
        }}
        
        .stat-footer {{
            padding: 15px 20px;
            background: #f9f7f2;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: space-between;
        }}
        
        .stat-link {{
            color: #00927E;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            display: flex;
            align-items: center;
            transition: all 0.3s ease;
        }}
        
        .stat-link i {{
            margin-right: 5px;
        }}
        
        .stat-link:hover {{
            color: #007A68;
            text-decoration: underline;
        }}
        
        .dashboard-quick-actions {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            padding: 25px;
            margin-bottom: 30px;
        }}
        
        .dashboard-quick-actions h3 {{
            margin: 0 0 20px 0;
            color: #333;
            font-size: 18px;
            font-weight: 600;
            display: flex;
            align-items: center;
        }}
        
        .dashboard-quick-actions h3 i {{
            margin-right: 10px;
            color: #D4AF37;
        }}
        
        .quick-actions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .quick-action-card {{
            background: #f9f7f2;
            border-radius: 10px;
            padding: 20px;
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #333;
            transition: all 0.3s ease;
            border: 1px solid #eee;
        }}
        
        .quick-action-card:hover {{
            background: #00927E;
            color: white;
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .quick-action-icon {{
            width: 50px;
            height: 50px;
            background: white;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            color: #00927E;
            font-size: 20px;
            transition: all 0.3s ease;
        }}
        
        .quick-action-card:hover .quick-action-icon {{
            background: rgba(255,255,255,0.2);
            color: white;
        }}
        
        .quick-action-text h4 {{
            margin: 0 0 5px 0;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .quick-action-text p {{
            margin: 0;
            font-size: 13px;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-welcome {{
                flex-direction: column;
                text-align: center;
                padding: 20px;
            }}
            
            .welcome-icon {{
                margin-right: 0;
                margin-bottom: 15px;
            }}
            
            .stat-footer {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .quick-action-card {{
                flex-direction: column;
                text-align: center;
            }}
            
            .quick-action-icon {{
                margin-right: 0;
                margin-bottom: 10px;
            }}
        }}
    </style>
    """
    
    return mark_safe(html) 