from tip_app_main.views_helpers import *
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from tip_app_main.forms import ContactForm
from .models import Match, Tip
from users.models import Profile
from django.http import BadHeaderError, HttpResponse
from django.shortcuts import render
from tip_app.settings import EMAIL_HOST_USER, MEDIA_ROOT
from django.core.mail import send_mail
import json
from itertools import zip_longest
import csv
from datetime import timedelta
from django.utils import timezone

# -*- coding: utf-8 -*-

from django.http import JsonResponse


@login_required
@csrf_protect
def home(request):
    update_scores_and_ranks(request)
    mobile_agent = False
    users_ranked = Profile.objects.filter(rank__lte=5).order_by(
        '-score', '-right_tips', 'joker', 'user__username')
    if len(users_ranked) > 5:
        users_ranked = Profile.objects.filter(rank__lte=5).order_by(
            '-score', '-right_tips', 'joker', 'user__username')[:5]
    if request.user not in users_ranked:
        users_ranked.union(Profile.objects.filter(user=request.user))

    try:
        upcoming_match = Match.objects.filter(
            match_date__gte=timezone.now()).order_by('match_date')[0]
        time_diff = upcoming_match.match_date - timezone.now()
        days = time_diff.days
        hours = time_diff.seconds//3600
        minutes = (time_diff.seconds//60) % 60
        seconds = time_diff.seconds % 60
    except:
        upcoming_match = None
        time_diff = None
        days, hours, minutes, seconds = None, None, None, None
    try:
        tipps = Tip.objects.filter(author=request.user)
        tipps_by_matches = {t.match.pk: t for t in tipps}
    except:
        tipps = None
        tipps_by_matches = None
    if request.method == "GET" and request.is_ajax():
        upcoming_match_time = upcoming_match.match_date
        data = {}
        data['countdown_match'] = upcoming_match_time
        data = request.GET.get(upcoming_match_time)
        return JsonResponse({"upcoming_match_time": upcoming_match_time}, status=200)
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
        tipps = Tip.objects.filter(
            author=request.user).filter(match__matchday=m_nr)
        tipps_by_matches = {t.match.pk: t for t in tipps}
    except:
        tipps = None
        tipps_by_matches = None
    n_joker = get_n_joker(request.user, m_nr)
    matchday_match_ids_and_matchdates = get_match_ids_and_matchdates_for_matchday(
        m_nr)
    # match_dates = get_match_dates(m_nr)
    if request.method == 'POST' and request.is_ajax():
        body_unicode = request.body.decode('utf-8')
        received_json = json.loads(body_unicode)
        id = received_json['tip_id']
        value = received_json['tip_value']
        joker = received_json['joker']
        save_tip(id, value, joker, request.user, request)
        n_joker = get_n_joker(request.user, m_nr)
        return HttpResponse(json.dumps({'n_joker': n_joker, 'm_nr': m_nr,
                                        'matchday_matches_ids_and_matchdates': matchday_match_ids_and_matchdates,
                                        'match_array_length': len(matchday_match_ids_and_matchdates)}))
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
    ordered_matchday_matches = matchday_matches.order_by(
        'match_date', 'home_team__team_name')
    matchday_scores = update_scores_and_ranks(matchday_number)
    matchday_tips = Tip.objects.filter(match__matchday=matchday_number)
    users_ranked = Profile.objects.order_by(
        '-score', '-right_tips', 'joker', 'user__username')
    # get current match
    try:
        current_match = Match.objects.filter(
                match_date__lte=timezone.now().replace(microsecond=0) + timedelta(minutes=120)).order_by('-match_date')[0]
    except:
        # no matches then none else last one.
        if len(Match.objects.all()) == 0:
            current_match = None
        else: 
            current_match = Match.objects.all().order_by('match_date').last()
            
    context = {
        'ordered_matchday_matches': ordered_matchday_matches,
        'matchday_matches': matchday_matches,
        'matchday_number': matchday_number,
        'matchday_scores': matchday_scores,
        'current_match': current_match,
        'users_ranked': users_ranked,
        'matchday_tips': matchday_tips,
        'request_user': request.user,
    }
    return render(request, 'tip_app_main/results_per_day.html', context)


@login_required
def ranking(request):
    update_scores_and_ranks(request)
    users_ranked = Profile.objects.order_by(
        '-score', '-right_tips', 'joker', 'user__username')
    context = {
        'request_user': request.user,
        'users_ranked': users_ranked,
    }
    return render(request, 'tip_app_main/ranking.html', context)


@csrf_protect
@staff_member_required
@login_required
def email(request):
    recepients = []
    for user in Profile.objects.all():
        recepients.append(user.user.email)
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, EMAIL_HOST_USER,
                          recipient_list=recepients)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('tip-mail')
    return render(request, "tip_app_main/email.html", {'form': form})


@csrf_protect
@staff_member_required
@login_required
def reminder_email(request):
    try:
        upcoming_match = Match.objects.filter(
            match_date__gt=timezone.now().replace(microsecond=0)).order_by('match_date')[0]
        upcoming_matches = Match.objects.filter(matchday=upcoming_match.matchday).order_by('match_date')
    except:
        upcoming_match = None
        upcoming_matches = None
    for user in Profile.objects.all():
        not_tipped_matches = []
        for upcoming_match in upcoming_matches:
            try:
                tip = Tip.objects.get(author=user.user.id, match_id=upcoming_match.id)
            except:
                tip = None
            if not tip.match.has_started():
                if not tip or (tip.tip_home == -1 or tip.tip_guest == -1):
                    print(tip.match)
                    not_tipped_matches.append(upcoming_match)
        subject = 'WO SIND DEINE TIPPS DU PAPPNASE?'
        if len(not_tipped_matches) != 0:
            message = reminder_mail_message(not_tipped_matches)
            send_mail(subject,
               message, EMAIL_HOST_USER, recipient_list=[user.user.email])
            messages.success(request, 'Reminder an ' + user.user.email + ' gesendet!')
    return redirect('tip-mail')


@login_required
@csrf_protect
def pdf_view(request):
    with open(MEDIA_ROOT + '/WM2022onlineRegeln.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=TippspielRegeln2018.pdf'
        return response


@login_required
@csrf_protect
def csv_export(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="TippSpielReport.csv"'
    writer = csv.writer(response)
    try:
        profiles = Profile.objects.all()
    except:
        profiles = None
    if profiles != None:
        writer.writerow(['Rank', 'Spieler', 'Punkte',
                        'Joker', '6er', 'Weltmeister', ''])
        for profile in Profile.objects.order_by(
        '-score', '-right_tips', 'joker', 'user__username'):
            writer.writerow([profile.rank, profile.user.username, profile.score,
                            profile.joker, profile.right_tips, profile.Weltmeister, ' '])
        writer.writerow(['', '', '', '', '', '', ''])
        writer.writerow(['---Tipps---', '', '', '', '', '', ''])
        writer.writerow(['', '', '', '', '', '', ''])
        for profile in profiles:
            writer.writerow([str(profile.user.username), '', '', '', '', '', ''])
            profile_tips = Tip.objects.filter(
                author=profile.user.id).order_by('match__match_date')
            writer.writerow(
                ['Spiel', 'Tipp','Joker', 'Spieldatum', 'Spieltag', 'Tippdatum', 'Tippdatum - Matchdatum'])
            profile_tip_rows = []
            for profile_tip in profile_tips:
                profile_tip_rows.append([str(profile_tip.match.home_team.team_name) + ':' + str(profile_tip.match.guest_team.team_name),
                                         str(profile_tip.tip_home) + ':' + str(
                                             profile_tip.tip_guest), str(profile_tip.joker),  str(profile_tip.match.match_date),
                                         str(profile_tip.match.matchday), str(profile_tip.tip_date), str(show_too_late_tip(profile_tip.match.match_date, profile_tip.tip_date))])
            writer.writerows(profile_tip_rows)
    return response
