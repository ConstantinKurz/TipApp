from tip_app_main.views_helpers import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from tip_app_main.forms import ContactForm
from .models import Match, Tip
from users.models import Profile
from django.http import BadHeaderError, HttpResponse
from django.shortcuts import render
from tip_app.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import json
from datetime import timedelta
from django.utils import timezone

# -*- coding: utf-8 -*-

from django.http import JsonResponse


@login_required
@csrf_protect
def home(request):
    update_scores_and_ranks(request)
    mobile_agent = False
    users_ranked = Profile.objects.filter(rank__lte=5).order_by('-score','-right_tips', 'joker', 'user__username')
    if len(users_ranked) > 5: 
        users_ranked = Profile.objects.filter(rank__lte=5).order_by('-score','-right_tips', 'joker', 'user__username')[:5]
    if request.user not in users_ranked:
        users_ranked.union(Profile.objects.filter(user=request.user))

    try:
        upcoming_match = Match.objects.filter(
            match_date__gte=timezone.now()).order_by('match_date')[0]
        time_diff = upcoming_match.match_date - timezone.now()
        days = time_diff.days
        hours = time_diff.seconds//3600
        minutes = (time_diff.seconds//60)%60
        seconds = time_diff.seconds % 60
    except:
        upcoming_match = None
        time_diff = None
        days, hours, minutes, seconds = None
    try:
        tipps = Tip.objects.filter(author=request.user)
        tipps_by_matches = {t.match.pk: t for t in tipps}
    except:
        tipps=None
        tipps_by_matches = None
    # send mail if user has not tipped yet
    if upcoming_match and upcoming_match.half_hour_remaining():
        send_remainder_mail(upcoming_match)
    if request.method == "GET" and request.is_ajax():
        upcoming_match_time = upcoming_match.match_date
        #print(upcoming_match_time)
        data = {}
        data['countdown_match'] = upcoming_match_time
        data = request.GET.get(upcoming_match_time)
        # #print(request.GET.get(data))
        return JsonResponse({"upcoming_match_time": upcoming_match_time}, status = 200)
    if is_mobile(request):
        mobile_agent = True
    context = {
        'mobile_agent': mobile_agent,
        'time_diff': time_diff,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'users_ranked': users_ranked,
        'upcoming_match': upcoming_match,
        'tipps': tipps_by_matches,
        'request_user': request.user,
    }
    return render(request, 'tip_app_main/home.html', context)


@login_required
@csrf_protect
def tip_matchday(request, matchday_number):

    m_nr: int = int(matchday_number)
    matches_per_day = Match.objects.filter(
        matchday=m_nr).order_by('match_date')
    try:
        tipps = Tip.objects.filter(author=request.user).filter(match__matchday=m_nr)
        tipps_by_matches = {t.match.pk: t for t in tipps}
        # print('tipps_match: ', tipps_by_matches)
    except:
        tipps = None
        tipps_by_matches = None
    n_joker = get_n_joker(request.user, m_nr)
    # print('n_joker', n_joker)
    matchday_matches_ids = get_match_ids_for_matchday(m_nr)
    if request.method == 'POST' and request.is_ajax():
        body_unicode = request.body.decode('utf-8')
        received_json = json.loads(body_unicode)
        id = received_json['tip_id']
        value = received_json['tip_value']
        joker = received_json['joker']
        save_tip(id, value, joker, request.user, request)
        n_joker = get_n_joker(request.user, m_nr)
        # print('id', id)
        # print('value', value)
        # print('n_joker_post', n_joker)
        return HttpResponse(json.dumps({'n_joker': n_joker, 'm_nr': m_nr, 'matchday_matches_ids': matchday_matches_ids})) 
    context = {
            'number': m_nr,
            'matches_per_day': matches_per_day,
            'tips': tipps_by_matches,
            'n_joker': n_joker,
        }
    return render(request, 'tip_app_main/matchday.html', context)

@login_required
@csrf_protect
def results(request, matchday_number):
    """
    zeige ergebnisse und tips nach spieltag
    :param request:
    :param matchday_number:
    :return:
    """
    matchday_number: int = int(matchday_number)
    matchday_matches = Match.objects.filter(matchday=matchday_number)
    ordered_matchday_matches = matchday_matches.order_by('match_date')
    matchday_scores = update_scores_and_ranks(request, matchday_number)
    matchday_tips = Tip.objects.filter(match__matchday=matchday_number)
    users_ranked = Profile.objects.order_by('-score','-right_tips', 'joker', 'user__username')

    context = {
        'ordered_matchday_matches': ordered_matchday_matches,
        'matchday_matches': matchday_matches,
        'matchday_number': matchday_number,
        'matchday_scores': matchday_scores,
        'users_ranked': users_ranked,
        'matchday_tips': matchday_tips,
        'request_user': request.user,
    }
    return render(request, 'tip_app_main/results_per_day.html', context)

@login_required
def ranking(request):
    update_scores_and_ranks(request)
    users_ranked = Profile.objects.order_by('-score','-right_tips', 'joker', 'user__username')
    context = {
        'request_user': request.user,
        'users_ranked': users_ranked,
    }
    return render(request, 'tip_app_main/ranking.html', context)

# def champion(request):
#     # do it with twp checkboxes
#     if request.method == 'POST':
#         for k, v in request.POST.items():
#             team_id = k[5]
#             team = Team.objects.get(team__id = team_id)
#             #print("champion:", team)
#             #print('k_champion:', k)
#             #print('v_champion:', v)
#             if k.startswith('out_'):
#                 #print("-----------")
#                 team.eliminated = 1
#             else:
#                 champion.eliminated = 0
#                 #print(champion.eliminated)
#             champion.save()    
#         messages.success(request, 'Gespeichert!')
#         return HttpResponseRedirect(reverse('tip-champion'))
#     teams = Team.objects.all()
#     context = {
#         'teams': teams,
#     }
#     return render(request, 'tip_app_main/champion.html', context)


# @staff_member_required
# @csrf_protect
# def reminder_email(request):
#     """
#     send email to profiles which haven't tipped for next match yet.
#     :param request:
#     :return:
#     """
#     not_tipped = []
#     next_match = Match.objects.filter(
#         match_date__gte=timezone.now()).order_by('match_date')[0]
#     for user in Profile.objects.all():
#         try:
#             tipp = Tip.objects.get(author=user.user.id, match_id=next_match.id)

#         except:
#             tipp = None
#             # #print(user.user.email)
#         if not tipp:
#             not_tipped.append(user.user.email)
#             # #print("not_tipped:", not_tipped)
#     subject = 'WO SIND DEINE TIPPS DU ARSCH?'
#     message = 'LIES DEN BETREFF DU IDIOT UND TIPPEN KANNST DU HIER: https://django-tipapp.herokuapp.com/'

    #print(subject)
    #print(message)
    # recepients = not_tipped
    # if not_tipped:
    #     send_mail(subject,
    #               message, EMAIL_HOST_USER, recipient_list=recepients, fail_silently=False)
    # return HttpResponseRedirect(reverse('tip-mail'))


@csrf_protect
@staff_member_required
@login_required
def email(request):
    recepients = []
    for user in Profile.objects.all():
        recepients.append(user.user.email)
    #print(recepients)
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            #print(subject)
            #print(messages)
            try:
                send_mail(subject, message, EMAIL_HOST_USER,
                          recipient_list=recepients)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('tip-mail')
    return render(request, "tip_app_main/email.html", {'form': form})
