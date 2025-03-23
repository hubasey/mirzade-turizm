from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main.admin import admin_site
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('main.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('editor/', include('editor.urls')),  # Editör paneli URL'leri
    path('accounts/login/', RedirectView.as_view(url='/editor/login/', permanent=True)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 