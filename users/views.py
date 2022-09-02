from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from tip_app_main.models import Match
from tip_app.settings import EMAIL_HOST_USER
from .forms import UserRegisterForm
from .forms import UserUpdateForm
from .forms import ProfileUpdateForm
from django.core.mail import send_mail


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account für {username} erstellt!')
            subject = "Willkommen bei ShortyTipp!"
            message = f'Hi {username}'
            send_mail(subject,
                      message, EMAIL_HOST_USER, recipient_list=[form.cleaned_data.get('email')], fail_silently=False)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    try:
        first_match = Match.objects.order_by('match_date')[0]
    except:
        first_match = None
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            if 'Weltmeister' in p_form.cleaned_data and first_match.has_started():
                messages.warning(request, 'Das erste Spiel hat schon begonnen. Keine Änderung des Weltmeisters mehr möglich!')
                return redirect('profile')
            else:
                u_form.save()
                p_form.save()
                messages.success(request, 'Account wurde aktualisiert!')
                return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/profile.html', context)