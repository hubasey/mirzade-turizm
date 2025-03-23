from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from functools import wraps
from main.models import Tour, BlogPost, TourReservation, Slider

def is_editor(user):
    """Kullanıcının Editor grubuna ait olup olmadığını kontrol eder."""
    return user.groups.filter(name='Editor').exists()

def editor_required(view_func):
    """Kullanıcının editor olup olmadığını kontrol eden decorator."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Bu sayfaya erişmek için giriş yapmalısınız.")
            return redirect('/editor/login/')
        if not is_editor(request.user):
            messages.error(request, "Bu sayfaya erişim yetkiniz bulunmamaktadır.")
            return redirect('/editor/login/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def editor_login(request):
    """Editör giriş sayfası."""
    if request.user.is_authenticated:
        return redirect('editor:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if is_editor(user) or user.is_superuser:
                    login(request, user)
                    messages.success(request, f"Hoş geldiniz, {username}!")
                    return redirect('editor:dashboard')
                else:
                    messages.error(request, "Bu hesabın editör paneline erişim yetkisi bulunmamaktadır.")
            else:
                messages.error(request, "Geçersiz kullanıcı adı veya şifre.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'editor/login.html', {'form': form})

def editor_logout(request):
    """Editör çıkış fonksiyonu."""
    logout(request)
    messages.success(request, "Başarıyla çıkış yaptınız.")
    return redirect('editor:login')

@editor_required
def editor_dashboard(request):
    """Editör kontrol paneli."""
    tour_count = Tour.objects.count()
    blog_count = BlogPost.objects.count()
    reservation_count = TourReservation.objects.count()
    slider_count = Slider.objects.count()
    
    context = {
        'tour_count': tour_count,
        'blog_count': blog_count,
        'reservation_count': reservation_count,
        'slider_count': slider_count,
    }
    return render(request, 'editor/dashboard.html', context)

@editor_required
def tour_list(request):
    """Tur listesi sayfası."""
    tours = Tour.objects.all().order_by('-date')
    return render(request, 'editor/tour_list.html', {'tours': tours})

@editor_required
def slider_list(request):
    """Slider listesi sayfası."""
    sliders = Slider.objects.all().order_by('order')
    return render(request, 'editor/slider_list.html', {'sliders': sliders})

@editor_required
def reservation_list(request):
    """Rezervasyon listesi sayfası."""
    reservations = TourReservation.objects.all().order_by('-created_at')
    return render(request, 'editor/reservation_list.html', {'reservations': reservations})
