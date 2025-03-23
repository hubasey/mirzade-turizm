from .models import SiteSettings

def site_settings(request):
    """
    Site ayarlarını tüm şablonlara ekler.
    """
    try:
        settings = SiteSettings.objects.first()
        return {'site_settings': settings}
    except:
        return {'site_settings': None} 