from django.utils import timezone
from users.models import Profile
from .models import Tip, Match
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from tip_app.settings import EMAIL_HOST_USER

def save_tip(id, value, joker,  user, request):
        match_id = id.split('_', -1)[-1]
        match = get_object_or_404(Match, pk=match_id)
        try: 
            tip = Tip.objects.get(author=user, match__id=match_id)
        except:
            tip = None
        if 'home' in id:
            new_home_tip(tip, match, value, user)   
        if 'guest' in id: 
            new_guest_tip(tip, match, value, user)    
        if 'joker' in id:
            new_joker(tip, match, joker, user)  
     

def new_home_tip(tip, match, value, user):
    if validate_input(value):
        if tip:
            tip.tip_date = timezone.now()
            tip.tip_home = value
        else:
            tip = Tip(
                tip_date = timezone.now(),
                author = user,
                match = match,
                tip_home = value,
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
                tip_date = timezone.now(),
                author = user,
                match = match,
                tip_guest = value,
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
            tip_date = timezone.now(),
            author = user,
            match = match,
            tip_joker = value,
        )
    is_joker_valid(match.matchday, get_n_joker(user, match.matchday), tip)
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
    if int(value) > -1:
        return True
    else:
        False

def get_match_ids_and_matchdates_for_matchday(matchday_number):
    match_ids_and_dates = {}
    matchday_matches = Match.objects.filter(matchday=matchday_number).order_by('match_date')
    for match in matchday_matches:
        match_ids_and_dates[match.id] = match.match_date.strftime("%Y-%m-%dT%H:%M:%S")
    return match_ids_and_dates

# def get_match_dates(matchday_number):
#     match_dates = []
#     matchday_matches = Match.objects.filter(matchday=matchday_number).order_by('match_date')
#     for match in matchday_matches:
#         match_dates.append(match.matchdate)
#     return match_dates

def update_scores_and_ranks(matchday=None):
    matchday_tipps_per_user = {}
    for user in Profile.objects.all():
        if (Tip.objects.filter(author=user.user)):
            user.update_score_and_joker()
        if matchday != None:
            matchday_tipps_per_user[user.user.id] = user.get_score_and_joker_for_matchday(matchday)
        user.save()

    # update ranks
    users_ranked = Profile.objects.order_by('-score','-right_tips', 'joker')
    # order users dirty
    temp_rank = 1
    for index, user in enumerate(users_ranked):
        if index > 0:
            # account for same values
            if users_ranked[index-1].score == user.score and users_ranked[index-1].right_tips == user.right_tips \
                and users_ranked[index-1].joker == user.joker:
                temp_rank-=1
        user.rank=temp_rank
        user.save()
        temp_rank+=1
    return matchday_tipps_per_user

def is_mobile(request):
    user_agent = request.META['HTTP_USER_AGENT']
    return 'Mobile' in user_agent