from django.shortcuts import render, redirect
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



# Create your views here.
def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the username is valid
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nombre de usuario ya en uso')
            return redirect('sign_up')

        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            profile = Profile(user=user)
            profile.save()
            login(request, user)
            messages.success(request, 'Nueva cuenta creada')
            return redirect('search')
        except Exception as e:
            messages.error(request, f'Ocurrió un error: {e}')

    return render(request, 'users/sign_up.html')

def log_in(request):
    if request.method == 'POST':
        user_ = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=user_, password=password)

        if user is not None:
            login(request, user)
            groups = user.groups.all()
            if groups:
                request.session['role'] = groups[0].name
            else:
                request.session['role'] = 'user'
            messages.success(request,'Autenticación exitosa')
            return redirect('search')
        else:
            messages.error(request, 'Credenciales inválidas')
            return redirect('log_in')
    return render(request, 'users/log_in.html')

def log_out(request):
    logout(request)
    request.session['role'] = 'user'
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('search')

def about(request):
    return render(request, 'base/about.html')