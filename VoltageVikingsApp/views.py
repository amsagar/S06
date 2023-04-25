from django.shortcuts import render, redirect
from .models import UserProfile, Requests

lat, long = 0, 0
src_lat, src_long = 0, 0


def landing_page_view(request):
    if request.user.is_authenticated:
        return redirect('/home')
    return render(request, 'index.html')


def home_page(request):
    profile = UserProfile.objects.get(user=request.user)
    try:
        user_requests = Requests.objects.filter(to_user=profile, accepted=True)
    except:
        user_requests = None
    return render(request, 'main/home_page.html',
                  {'profile': profile, 'message': 'LOGIN SUCCESSFULL!!!', 'req': user_requests})

