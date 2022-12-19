from cmath import e
from django.utils import timezone
from datetime import timedelta
from users.models import Profile
from .models import Tip, Match
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from tip_app.settings import EMAIL_HOST_USER


def save_tip(id, value, joker,  user, request):
    print('hier ist was da!!!!')
    match_id = id.split('_', -1)[-1]
    match = get_object_or_404(Match, pk=match_id)
    try:
        # dont save if already started.
        tip = Tip.objects.get(author=user, match__id=match_id)
        if tip.match.has_started():
            return
        if 'home' in id:
            new_home_tip(tip, match, value, user)
        if 'guest' in id:
            new_guest_tip(tip, match, value, user)
        if 'joker' in id:
            new_joker(tip, match, joker, user)
    except:
        tip = None


def new_home_tip(tip, match, value, user):
    if validate_input(value):
        if tip:
            tip.tip_date = timezone.now()
            tip.tip_home = value
        else:
            tip = Tip(
                tip_date=timezone.now(),
                author=user,
                match=match,
                tip_home=value,
            )
        tip.save()
    else:
        return


def new_guest_tip(tip, match, value, user):
    if validate_input(value):
        if tip:
            tip.tip_date = timezone.now()
            tip.tip_guest = value
        else:
            tip = Tip(
                tip_date=timezone.now(),
                author=user,
                match=match,
                tip_guest=value,
            )
        tip.save()
    else:
        return


def new_joker(tip, match, value, user):
    if tip:
        tip.tip_date = timezone.now()
        tip.joker = value
    else:
        tip = Tip(
            tip_date=timezone.now(),
            author=user,
            match=match,
            tip_joker=value,
        )
    is_joker_valid(match.matchday, get_n_joker(user, match.matchday), tip)
    tip.save()

def create_empty_tips(request):
    '''
    Helper func since some frontend functionalities need a tip for all matches.
    Creates empty tip if new match has been added.
    '''
    profiles = Profile.objects.all()
    matches = Match.objects.all()
    for profile in profiles:
        user_tips = Tip.objects.filter(author=profile.user.id)
        if (len(user_tips) != len(matches)):
            for match in matches:
                try: 
                    tip = Tip.objects.get(author=profile.user, match__id=match.id)
                except:
                    tip = Tip(
                        author=profile.user,
                        match=match,
                    )
                    tip.save()
    

def is_joker_valid(matchday_number, njoker, tip):
    if matchday_number < 3 and njoker > 3:
        tip.joker = False
    if matchday_number == 3 and njoker > 1:
        tip.joker = False
    if matchday_number == 4 and njoker > 1:
        tip.joker = False
    if matchday_number > 4 and njoker > 1:
        tip.joker = False


def get_n_joker(user, matchday_number):
    n_joker = 0
    if (matchday_number < 3):
        tips = Tip.objects.filter(
            author=user).filter(match__matchday__lt=3).order_by('match__match_date')
    if (matchday_number == 3):
        tips = Tip.objects.filter(
            author=user).filter(match__matchday=3).order_by('match__match_date')
    if (matchday_number == 4):
        tips = Tip.objects.filter(
            author=user).filter(match__matchday=4).order_by('match__match_date')
    if (matchday_number > 4):
        tips = Tip.objects.filter(
            author=user).filter(match__matchday__gt=4).order_by('match__match_date')
    for tip in tips:
        if tip.joker:
            n_joker += 1
    # asynchrone abgabe ist nicht gespeichert. dewegen muss hier
    # plus/minus 1 berücksichtigt werden.
    return n_joker


def validate_input(value):
    return int(value) > -1


def get_match_ids_and_matchdates_for_matchday(matchday_number):
    match_ids_and_dates = {}
    matchday_matches = Match.objects.filter(
        matchday=matchday_number).order_by('match_date')
    for match in matchday_matches:
        match_ids_and_dates[match.id] = match.match_date.strftime(
            "%Y-%m-%dT%H:%M:%S")
    return match_ids_and_dates

# def get_match_dates(matchday_number):
#     match_dates = []
#     matchday_matches = Match.objects.filter(matchday=matchday_number).order_by('match_date')
#     for match in matchday_matches:
#         match_dates.append(match.matchdate)
#     return match_dates


def update_scores_and_ranks(matchday=None):
    matchday_tipps_per_user = {}
    last_match = Match.objects.latest('match_date')
    last_match_not_finished = True
    # timezone.now().replace(microsecond=0) < \
    #         (last_match.match_date.replace(microsecond=0) + timedelta(minutes=150))
    for user in Profile.objects.all():
        if (Tip.objects.filter(author=user.user)):
            user.update_score_and_joker()
        if matchday != None:
            matchday_tipps_per_user[user.user.id] = user.get_score_and_joker_for_matchday(
                matchday)
            # do not save if last game is over and results are set
            if last_match_not_finished or (last_match.home_score == -1 or last_match.guest_score == -1):
                user.save()
    # update ranks
    users_ranked = Profile.objects.order_by('-score', '-right_tips', 'joker')
    # order users dirty
    temp_rank = 1
    for index, user in enumerate(users_ranked):
        if index > 0:
            # account for same values
            if users_ranked[index-1].score == user.score and users_ranked[index-1].right_tips == user.right_tips \
                    and users_ranked[index-1].joker == user.joker:
                temp_rank -= 1
        user.rank = temp_rank
        user.save()
        temp_rank += 1
    return matchday_tipps_per_user


def is_mobile(request):
    user_agent = request.META['HTTP_USER_AGENT']
    return 'Mobile' in user_agent


def reminder_mail_message(not_tipped_matches: list):
    message = 'Folgende Tipps für den aktuellen Spieltag fehlen noch: \n \n'
    message += '=========================\n\n'
    # if len(not_tipped_matches) == 0:
    #     return False, message
    for match in not_tipped_matches:
        message += '' + str(match.match_date) + ' \n \n'
        message += str(match.home_team) + ' : ' + \
            str(match.guest_team) + '\n\n'
        message += '=========================\n\n'
    message += 'Tippen kannst du hier: https://www.shortytipp.de'

    return message

def show_too_late_tip(match_date, tip_date):
        if (tip_date.replace(microsecond=0) - match_date.replace(microsecond=0)).total_seconds() > 0: 
            return tip_date - match_date
        return "--"

def points_cumsum(tips, tip_index):
    cumsum_points = 0
    for i in tips[:tip_index+1]:
        cumsum_points += i.points()
    return cumsum_points
