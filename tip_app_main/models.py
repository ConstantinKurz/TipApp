from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class Team(models.Model):
    team_name = models.CharField(max_length=100)
    team_ccode = models.CharField(max_length=3)
    win_points = models.IntegerField(default=10)
    eliminated = models.BooleanField(default=0)

    def __str__(self):
        return self.team_name


class Match(models.Model):
    home_team = models.ForeignKey(Team, related_name="home_team", on_delete=models.CASCADE, default=0)
    guest_team = models.ForeignKey(Team, related_name="guest_team", on_delete=models.CASCADE, default=0)
    match_date = models.DateTimeField(default=timezone.now)
    matchday = models.IntegerField(default=0)
    home_score = models.IntegerField(default=-1)
    guest_score = models.IntegerField(default=-1)


    def has_started(self):
        return self.match_date < timezone.now() + timedelta(seconds=180)

    def half_hour_remaining(self):
        return timezone.now().replace(microsecond=0) == (self.match_date - timedelta(seconds=30*60)).replace(microsecond=0)

    def __str__(self):
        return 'Match: ' + self.home_team.team_name + ' : ' + self.guest_team.team_name \
            + ' | Spieltag: ' + str(self.matchday)

class Tip(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.PROTECT)
    tip_date = models.DateTimeField(default=timezone.now)
    tip_home = models.IntegerField(default=-1)
    tip_guest = models.IntegerField(default=-1)
    joker = models.BooleanField(default=False)

    def __str__(self):
        return 'Author:' + str(self.author) + ' | Match: ' + self.match.home_team.team_name + ' : ' + self.match.guest_team.team_name \
            + ' | Spieltag: ' + str(self.match.matchday) +  ' | Tipp-Datum: ' + str(self.tip_date)
    

    def points(self):
        sh = self.match.home_score
        sg = self.match.guest_score
        th = self.tip_home
        tg = self.tip_guest
        # no tip
        sgn = lambda x: 0 if x == 0 else x / abs(x)
        if -1 in [sh, sg, th, tg]:
            return 0
        points = 0
        ds = sh - sg
        dt = th - tg
        # print(self.match)
        # print(self.author)
        if sgn(ds) == sgn(dt):
            # print("tendenz richtig:")
            # print("------------")
            # print(sh,sg,th,tg, ds, dt )
            # print(sgn(ds))
            # print(sgn(dt))
            #correct tendency
            points += 3
            # print(points)
        if sh == th or sg == tg:
            points += 1
            # print("===========================")
            # print("ein ergbniss richtig")
            # print("points", points)
        if sh == th and sg == tg: 
            # print("beide ergebnisse richtig")
            points += 1
            # print("points", points)
        if ds == dt:
            #correct difference
            # print("differenz")
            points += 1
            # print(points)
        if self.joker: 
            points *= 2
        return points
        #TODO: multiplicator nicht vergessen
    
    def matchday_multiplicator(self, points):
        if  2 < self.match.matchday < 5:
            points*=2
        if  self.match.matchday > 4:
            points*=3
        return points