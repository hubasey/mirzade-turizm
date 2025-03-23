from django.urls import path
from . import views

app_name = 'editor'

urlpatterns = [
    path('', views.editor_dashboard, name='dashboard'),
    path('login/', views.editor_login, name='login'),
    path('logout/', views.editor_logout, name='logout'),
    path('tours/', views.tour_list, name='tour_list'),
    path('sliders/', views.slider_list, name='slider_list'),
    path('reservations/', views.reservation_list, name='reservation_list'),
] 