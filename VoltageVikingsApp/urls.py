from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.landing_page),
    path('account/', include('allauth.urls')),
    path('captcha/', include('captcha.urls')),
    path('home/', views.landing_page),
]
