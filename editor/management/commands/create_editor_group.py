from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from main.models import BlogPost, Tour, Slider, TourReservation

class Command(BaseCommand):
    help = 'Editör grubu oluşturur ve gerekli izinleri atar'

    def handle(self, *args, **options):
        # Editör grubu oluştur veya mevcut grubu al
        editor_group, created = Group.objects.get_or_create(name='Editor')
        
        if created:
            self.stdout.write(self.style.SUCCESS('Editör grubu başarıyla oluşturuldu.'))
        else:
            self.stdout.write(self.style.WARNING('Editör grubu zaten mevcut. İzinler güncellenecek.'))
            
        # Tüm izinleri temizle
        editor_group.permissions.clear()
        
        # İzin verilecek modeller
        models = [
            (BlogPost, ['view', 'add', 'change']),
            (Tour, ['view', 'add', 'change']),
            (Slider, ['view', 'add', 'change']),
            (TourReservation, ['view', 'change']),
        ]
        
        # Her model için izinleri ekle
        for model, actions in models:
            content_type = ContentType.objects.get_for_model(model)
            for action in actions:
                codename = f"{action}_{model._meta.model_name}"
                try:
                    permission = Permission.objects.get(content_type=content_type, codename=codename)
                    editor_group.permissions.add(permission)
                    self.stdout.write(f"İzin eklendi: {codename}")
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"İzin bulunamadı: {codename}"))
        
        self.stdout.write(self.style.SUCCESS(f"Editör grubuna toplam {editor_group.permissions.count()} izin atandı.")) 