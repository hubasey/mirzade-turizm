# Generated by Django 5.1.6 on 2025-03-10 13:33

import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_title', models.CharField(max_length=100, verbose_name='Site Başlığı')),
                ('site_description', models.TextField(verbose_name='Site Açıklaması')),
                ('logo', main.models.OptimizedImageField(upload_to='site_settings/', verbose_name='Logo')),
                ('favicon', main.models.OptimizedImageField(upload_to='site_settings/', verbose_name='Favicon')),
                ('email', models.EmailField(max_length=254, verbose_name='E-posta')),
                ('phone', models.CharField(max_length=20, verbose_name='Telefon')),
                ('whatsapp', models.CharField(max_length=20, verbose_name='WhatsApp')),
                ('address', models.TextField(verbose_name='Adres')),
                ('facebook', models.URLField(blank=True, null=True, verbose_name='Facebook')),
                ('twitter', models.URLField(blank=True, null=True, verbose_name='Twitter')),
                ('instagram', models.URLField(blank=True, null=True, verbose_name='Instagram')),
                ('youtube', models.URLField(blank=True, null=True, verbose_name='YouTube')),
                ('linkedin', models.URLField(blank=True, null=True, verbose_name='LinkedIn')),
                ('meta_keywords', models.TextField(blank=True, null=True, verbose_name='Meta Anahtar Kelimeler')),
                ('meta_description', models.TextField(blank=True, null=True, verbose_name='Meta Açıklama')),
                ('google_analytics', models.CharField(blank=True, max_length=50, null=True, verbose_name='Google Analytics ID')),
                ('footer_text', models.TextField(blank=True, null=True, verbose_name='Alt Bilgi Metni')),
                ('copyright_text', models.CharField(blank=True, max_length=255, null=True, verbose_name='Telif Hakkı Metni')),
            ],
            options={
                'verbose_name': 'Site Ayarları',
                'verbose_name_plural': 'Site Ayarları',
            },
        ),
    ]
