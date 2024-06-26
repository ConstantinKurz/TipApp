from django.db import models
from django.contrib.auth.models import User
from tip_app_main.models import Tip, Team


class Profile(models.Model):

    champion_choices = [(team.team_ccode, team.team_name) for team in Team.objects.all()]
    #champion_choices = [('GER', 'Deutschland'), ('FRA', 'Frankreich')]
    champion_choices.append([('---'), ('---')])

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    score = models.IntegerField(default=0)
    right_tips = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    Europameister = models.CharField(max_length=12, choices=champion_choices, default='---')
    joker = models.IntegerField(default=0)

    def update_score_and_joker(self):
        tipps = Tip.objects.filter(author=self.user.id)
        joker = 0
        right_tips = 0
        tip_score = 0
        for tipp in tipps:
            #6er
            if tipp.joker and tipp.points() !=0:
                if tipp.points() / 2 % 6 == 0:
                    right_tips += 1      
            elif not tipp.joker and tipp.points() != 0: 
                if tipp.points() % 6 == 0: 
                    right_tips += 1
            #joker
            if tipp.joker and (tipp.match.has_started() or (tipp.match.guest_score != -1 and tipp.match.home_score != -1)):
                joker += 1
            tip_score += tipp.points()
        self.joker = joker
        self.score = tip_score
        self.right_tips = right_tips

    def get_score_and_joker_for_matchday(self, matchday):
        try:
            matchday_tipps = Tip.objects.filter(author=self.user.id).filter(match__matchday=matchday)
        except:
            matchday_tipps = []
        matchday_score = 0 
        tip_score = 0
        for tipp in matchday_tipps:
            tip_score = tipp.points()
            matchday_score += tip_score
        return matchday_score


    def __str__(self):
        return f'{self.user.username} Profile'



