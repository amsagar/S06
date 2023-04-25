from django.shortcuts import render, redirect
from .models import UserProfile, Requests, ChargingStations
import json
from django.http import JsonResponse
from geopy import distance
from .mixins import Directions
from django.conf import settings
from .forms import UserProfileForm

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


def map(request, dest_lat=None, dest_long=None, id=None, page=None):
    global src_lat, src_long
    if page == 0 and id:
        dest_user = ChargingStations.objects.get(id=id)
    else:
        dest_user = UserProfile.objects.get(id=id)
    if request.method == 'POST':
        data = json.loads(request.body)
        src_lat = float(data.get('latitude'))
        src_long = float(data.get('longitude'))
        directions = Directions(
            lat_a=src_lat,
            long_a=src_long,
            lat_b=dest_lat,
            long_b=dest_long
        )
        context = {
            "google_api_key": settings.GOOGLE_API_KEY,
            "lat_a": src_lat,
            "long_a": src_long,
            "lat_b": dest_lat,
            "long_b": dest_long,
            "origin": f'{src_lat}, {src_long}',
            "destination": f'{dest_lat}, {dest_long}',
            "directions": directions,
            "destuser": dest_user,
            "page": page,
        }
        return render(request, 'main/routemap.html', context)
    directions = Directions(
        lat_a=src_lat,
        long_a=src_long,
        lat_b=dest_lat,
        long_b=dest_long
    )
    context = {
        "google_api_key": settings.GOOGLE_API_KEY,
        "lat_a": src_lat,
        "long_a": src_long,
        "lat_b": dest_lat,
        "long_b": dest_long,
        "origin": f'{src_lat}, {src_long}',
        "destination": f'{dest_lat}, {dest_long}',
        "directions": directions,
        "destuser": dest_user,
        "page": page,
    }
    return render(request, 'main/routemap.html', context)


def live(request, src_lat_got=None, src_long_got=None, dest_lat=None, dest_long=None, page=None, txn_id=None):
    context = {
        "google_api_key": settings.GOOGLE_API_KEY,
        "origin": f'{src_lat_got}, {src_long_got}',
        "destination": f'{dest_lat}, {dest_long}',
        "page": page,
        "txn_id": txn_id
    }
    return render(request, "main/live.html", context)


def avail(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        isChecked = request.POST.get('isChecked')
        if isChecked == 'true':
            profile.available = True
            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Action performed successfully'})
        else:
            profile.available = False
            profile.save()
            return JsonResponse({'status': 'success', 'message': 'Action performed successfully'})


def update_profile_profilepage(request):
    try:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = None
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.completed_profile = True
                profile.save()
        user_data = UserProfile.objects.get(user=request.user)
        return render(request, 'main/profile.html', {'data': user_data, "user": request.user})
    except Exception as e:
        try:
            return render(request, 'main/profile.html', {'data': request.user})
        except:
            return render(request, 'main/profile.html', {'err': "No Data Found"})


def complete_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.completed_profile = True
            profile.save()
            return redirect('/profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'main/completeprofile.html', {'form': form})


def nearby_home(request):
    global long, lat
    if request.method == 'POST':
        data = json.loads(request.body)
        lat = float(data.get('latitude'))
        long = float(data.get('longitude'))
        dest_got = int(data.get('dest_got'))
        nearby_addresses = []
        for i in UserProfile.objects.exclude(user=request.user):
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
        return render(request, 'main/nearbyhome.html', context)
    nearby_addresses = []
    for i in UserProfile.objects.exclude(user=request.user):
        address_lat = i.lat
        address_lon = i.lon
        try:
            dist = round(distance.distance((lat, long), (address_lat, address_lon)).km, 2)
            if dist <= 5:
                addr = {'address': i, 'distance': dist}
                nearby_addresses.append(addr)
        except:
            pass
    return render(request, 'main/nearbyhome.html', {'stat': nearby_addresses})
