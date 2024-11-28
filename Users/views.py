from django.shortcuts import render
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        user.save()
        profile = Profile(user=user)
        profile.save()
        return render(request, 'base/main.html')
    return render(request, 'users/sign_up.html')

def log_in(request):
    if request.method == 'POST':
        user_ = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=user_, password=password)

        if user is not None:
            login(request, user)
            return render(request, 'base/main.html')
    return render(request, 'users/log_in.html')

def log_out(request):
    logout(request)
    return render(request, 'base/main.html')