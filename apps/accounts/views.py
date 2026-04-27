from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfessorRegistroForm, LoginForm
from .models import User


def registro_professor(request):
    if request.user.is_authenticated:
        return redirect('dashboard_professor')

    if request.method == 'POST':
        form = ProfessorRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bem-vindo(a), Prof. {user.first_name}! Sua conta foi criada com sucesso.')
            return redirect('dashboard_professor')
    else:
        form = ProfessorRegistroForm()

    return render(request, 'accounts/registro_professor.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_professor():
            return redirect('dashboard_professor')
        return redirect('area_aluno')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_professor():
                return redirect('dashboard_professor')
            return redirect('area_aluno')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_professor(request):
    if not request.user.is_professor():
        return redirect('area_aluno')
    from apps.groups.models import GrupoEstudo
    grupos = GrupoEstudo.objects.filter(professor=request.user).order_by('-criado_em')
    return render(request, 'accounts/dashboard_professor.html', {'grupos': grupos})
