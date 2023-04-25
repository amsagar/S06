from django.shortcuts import render, redirect
from .models import UserProfile, Requests, ChargingStations
import json
from django.http import JsonResponse
from geopy import distance

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


def get_location(request):
    user = request.user
    user_data = UserProfile.objects.get(user=user)
    if user_data.got_loc:
        return JsonResponse({'status': 'success', 'message': 'Action performed successfully'})
    else:
        if request.method == 'POST':
            data = json.loads(request.body)
            user_data.lat = float(data.get('latitude'))
            user_data.lon = float(data.get('longitude'))
            user_data.got_loc = True
            user_data.save()
            return JsonResponse({'status': 'success', 'message': 'Action performed successfully'})


def nearby_stat(request):
    global long, lat
    if request.method == 'POST':
        data = json.loads(request.body)
        lat = float(data.get('latitude'))
        long = float(data.get('longitude'))
        dest_got = int(data.get('dest_got'))
        nearby_addresses = []
        for i in ChargingStations.objects.all():
            address_lat = i.lat
            address_lon = i.lon
            try:
                dist = round(distance.distance((lat, long), (address_lat, address_lon)).km, 2)
                if dist <= dest_got:
                    addr = {'address': i, 'distance': dist}
                    nearby_addresses.append(addr)
            except:
                pass
        context = {'stat': nearby_addresses}
        return render(request, 'main/nearbystat.html', context)
    nearby_addresses = []
    for i in ChargingStations.objects.all():
        address_lat = i.lat
        address_lon = i.lon
        try:
            dist = round(distance.distance((lat, long), (address_lat, address_lon)).km, 2)
            if dist <= 25:
                addr = {'address': i, 'distance': dist}
                nearby_addresses.append(addr)
        except:
            pass
    context = {'stat': nearby_addresses}
    return render(request, 'main/nearbystat.html', context)
