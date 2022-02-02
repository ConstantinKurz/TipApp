from datetime import timedelta
from tip_app_main.models import Match, Tip
from django.utils import timezone
from django import template

register = template.Library()


@register.filter(name='lookup')
def lookup(dict, index):
    if index in dict:
        return dict[index]
    return None


@register.filter(name='current_matchday')
def current_matchday(matchday):
    next_matchday = Match.objects.filter(
        match_date__gte=timezone.now() + timedelta(seconds=150 * 60))
    return next_matchday.values('matchday')


@register.filter
def modulo(value, arg):
    return value % arg

@register.simple_tag
def joker_upper_limit_reached(matchday, njoker):
    if matchday < 3 and njoker == 3:
        return True
    if matchday == 3 and matchday < 5 and njoker == 1:
        return True
    if matchday == 4 and njoker == 1:
        return True
    if matchday > 4 and njoker == 1:
        return True

@register.simple_tag
def disable_joker(tip: Tip, match: Match, njoker):
    boolVariable = tip.joker or match.has_started()
    if (tip.tip_home == -1 or tip.tip_guest == -1):
        return True
    if joker_upper_limit_reached(matchday=match.matchday, njoker=njoker) and not boolVariable:
        return True
    return False

@register.simple_tag
def get_users_matchday_score(scores, user):
    return scores[user.user.id][0]


@register.simple_tag
def get_users_matchday_tips(matchday_tips, user, matchday):
    user_matchday_tips = matchday_tips.filter(author=user.user.id)
    matchday_matches = Match.objects.filter(matchday=matchday)
    if (len(matchday_matches) != len(user_matchday_tips)):
        for match in matchday_matches:
            try:
                tip = Tip.objects.get(author=user.user, match__id=match.id)
            except:
                tip = None
            if tip == None:
                tip = Tip(
                    author=user.user,
                    match=match,
                )
                tip.save()
    user_matchday_tips = matchday_tips.filter(author=user.user.id)
    return user_matchday_tips.order_by('match__match_date', 'match__home_team__team_name')


@register.simple_tag
def get_upcoming_match():
    try:
        upcoming_match = Match.objects.filter(
            match_date__gte=timezone.now()).order_by('match_date')[0]
    except:
        return None
    return upcoming_match
