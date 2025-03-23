from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import os

class ImageFieldMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            # Tüm context verilerini kontrol et
            for key, value in response.context_data.items():
                # Tour nesnelerini kontrol et
                if key == 'tour' and hasattr(value, 'image'):
                    # Görsel var mı kontrol et
                    if not value.image or not value.image.name:
                        # Varsayılan görsel yolu ekle
                        setattr(value, '_default_image', '/static/images/default-tour.jpg')
                        
                        # Varsayılan görsel dosyası var mı kontrol et
                        default_image_path = os.path.join(settings.STATIC_ROOT, 'images', 'default-tour.jpg')
                        if not os.path.exists(default_image_path):
                            # Varsayılan görsel yoksa oluştur
                            try:
                                from PIL import Image, ImageDraw
                                img = Image.new('RGB', (800, 600), color=(100, 100, 150))
                                d = ImageDraw.Draw(img)
                                d.text((400, 300), 'Tur Görseli', fill=(255, 255, 255))
                                
                                # Dizin yoksa oluştur
                                os.makedirs(os.path.dirname(default_image_path), exist_ok=True)
                                img.save(default_image_path)
                            except:
                                pass  # PIL kütüphanesi yoksa sessizce devam et
        return response 