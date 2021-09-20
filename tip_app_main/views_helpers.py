from django.utils import timezone
from users.models import Profile
from .models import Tip, Match
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from tip_app.settings import EMAIL_HOST_USER

def save_tip(id, value, joker,  user, request):
        # print("#####save_tip#####")
        # print(id, value, joker, user, request )
        # print(id.split('_', -1))
        match_id = id.split('_', -1)[-1]
        # print(match_id)
        match = get_object_or_404(Match, pk=match_id)
        # print(match_id, match)
        try: 
            tip = Tip.objects.get(author=user, match__id=match_id)
        except:
            tip = None
        # print('match', match)
        # print('tip', tip)     
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
    #print(value) 
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
    if matchday_number >= 3 and matchday_number < 5 and njoker > 2:
        tip.joker = False
    if matchday_number >= 5 and njoker > 1:
        tip.joker = False

# def set_joker_false(tip: Tip):
#     tip.joker = False
#     tip.save()

def get_n_joker(user, matchday_number):
    n_joker = 0
    if (matchday_number < 3):
        tips = Tip.objects.filter(
        author=user).filter(match__matchday__lt=3).order_by('match__match_date')
    if (matchday_number >= 3 and matchday_number < 5):
        tips = Tip.objects.filter(
        author=user).filter(match__matchday__gte=3).filter(match__matchday__lt=5).order_by('match__match_date')
    if (matchday_number >= 5):
        tips = Tip.objects.filter(
        author=user).filter(match__matchday__gte=5).order_by('match__match_date')
    for tip in tips:
        if tip.joker:
            n_joker += 1
    # asynchrone abgabe ist nicht gespeichert. dewegen muss hier
    # plus/minus 1 berücksichtigt werden. 
    # if value == False and n_joker > 0: n_joker -= 1
    # if value: n_joker += 1
    return n_joker


def validate_input(value):
    return int(value) > -1

def get_match_ids_for_matchday(matchday_number):
    match_ids = []
    matchday_matches = Match.objects.filter(matchday=matchday_number).order_by('match_date')
    for match in matchday_matches:
        match_ids.append(match.id)
    return match_ids

def update_scores_and_ranks(request, matchday=None):
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


def send_remainder_mail(upcoming_match):
    not_tipped = []
    for user in Profile.objects.all():
        try:
            tip = Tip.objects.get(author=user.user.id, match_id=upcoming_match.id)
        except:
            tip = None
        if not tip or tip.tip_home == -1:
            not_tipped.append(user.user.email)
    subject = 'WO SIND DEINE TIPPS DU PAPPNASE?'
    message = 'TIPPEN KANNST DU HIER: https://www.shortytipp.de'
    recepients = not_tipped
    if not_tipped:
        send_mail(subject,
                  message, EMAIL_HOST_USER, recipient_list=recepients, fail_silently=False)

def is_mobile(request):
    user_agent = request.META['HTTP_USER_AGENT']
    # print(user_agent)
    # print('Mobile' in user_agent)
    return 'Mobile' in user_agent