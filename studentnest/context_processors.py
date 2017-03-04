from django.conf import settings
from django.contrib.auth.models import User
from studentnest.models import Profile
from django.shortcuts import get_object_or_404

def google_map_api(request):
    return {'MAP_KEY': settings.GOOGLE_MAP_KEY}

def profile(request):
    if not request.user.is_authenticated:
	return {'profile': None}
    profile = get_object_or_404(Profile, user=request.user)
    return {'profile': profile}
