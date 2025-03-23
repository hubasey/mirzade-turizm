from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter(name='add_days')
def add_days(value, days):
    """
    Verilen tarihe belirtilen gün sayısını ekler.
    Kullanım: {{ tarih|add_days:5 }}
    """
    try:
        if isinstance(value, str):
            # Eğer string formatında bir tarih geldiyse, önce datetime'a çevirelim
            try:
                value = datetime.strptime(value, "%d %b")
            except ValueError:
                # Farklı format denemeleri
                try:
                    value = datetime.strptime(value, "%d %B")
                except ValueError:
                    return value  # Çevrilemiyorsa olduğu gibi döndür
        
        # Gün sayısını integer'a çevirmeye çalış
        days = int(days)
        
        # Tarihe gün ekle
        new_date = value + timedelta(days=days)
        
        # Aynı formatta geri döndür (gün ve ay kısaltması)
        return new_date.strftime("%d %b")
    except (ValueError, TypeError):
        return value  # Herhangi bir hata durumunda orijinal değeri döndür 

@register.filter(name='turkce_tarih')
def turkce_tarih(value, format_str="d M"):
    """
    Tarihi Türkçe ay isimleriyle formatlar.
    Kullanım: {{ tarih|turkce_tarih:"d M" }}
    """
    if not value:
        return ""
    
    # Tarihi önce standart formatta formatla
    try:
        # Gün ve ay için ayrı formatla
        day = value.strftime("%d")
        month_num = value.month
        
        # Türkçe ay isimleri
        tr_months = {
            1: "Oca",
            2: "Şub",
            3: "Mar",
            4: "Nis",
            5: "May",
            6: "Haz",
            7: "Tem",
            8: "Ağu",
            9: "Eyl",
            10: "Eki",
            11: "Kas",
            12: "Ara"
        }
        
        # Türkçe ay ismini al
        month_tr = tr_months[month_num]
        
        # Formatı oluştur
        if format_str == "d M":
            return f"{day} {month_tr}"
        else:
            # Diğer formatlar için
            formatted_date = value.strftime(format_str)
            
            # İngilizce ay isimlerini Türkçe karşılıklarıyla değiştir
            eng_months = {
                "Jan": "Oca",
                "Feb": "Şub",
                "Mar": "Mar",
                "Apr": "Nis",
                "May": "May",
                "Jun": "Haz",
                "Jul": "Tem",
                "Aug": "Ağu",
                "Sep": "Eyl",
                "Oct": "Eki",
                "Nov": "Kas",
                "Dec": "Ara"
            }
            
            # Uzun ay isimleri için
            eng_months_long = {
                "January": "Ocak",
                "February": "Şubat",
                "March": "Mart",
                "April": "Nisan",
                "May": "Mayıs",
                "June": "Haziran",
                "July": "Temmuz",
                "August": "Ağustos",
                "September": "Eylül",
                "October": "Ekim",
                "November": "Kasım",
                "December": "Aralık"
            }
            
            # Kısa ay isimlerini değiştir
            for eng, tr in eng_months.items():
                formatted_date = formatted_date.replace(eng, tr)
            
            # Uzun ay isimlerini değiştir
            for eng, tr in eng_months_long.items():
                formatted_date = formatted_date.replace(eng, tr)
            
            return formatted_date
    except:
        return str(value)  # Herhangi bir hata durumunda orijinal değeri string olarak döndür

@register.filter(name='add_days_tr')
def add_days_tr(value, days):
    """
    Verilen tarihe belirtilen gün sayısını ekler ve Türkçe formatlar.
    Kullanım: {{ tarih|add_days_tr:5 }}
    """
    try:
        if isinstance(value, str):
            # Eğer string formatında bir tarih geldiyse, önce datetime'a çevirelim
            try:
                value = datetime.strptime(value, "%d %b")
            except ValueError:
                # Farklı format denemeleri
                try:
                    value = datetime.strptime(value, "%d %B")
                except ValueError:
                    return value  # Çevrilemiyorsa olduğu gibi döndür
        
        # Gün sayısını integer'a çevirmeye çalış
        days = int(days)
        
        # Tarihe gün ekle
        new_date = value + timedelta(days=days)
        
        # Türkçe formatla
        return turkce_tarih(new_date, "d M")
    except:
        return value  # Herhangi bir hata durumunda orijinal değeri döndür 