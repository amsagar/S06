from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.landing_page_view),
    path('account/', include('allauth.urls')),
    path('captcha/', include('captcha.urls')),
    path('home/', views.home_page),
    path('getlocation/', views.get_location),
    path('nearbystations/', views.nearby_stat),
]
