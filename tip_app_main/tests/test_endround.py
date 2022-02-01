from datetime import datetime
from users.signals import create_profile
from django.test import TestCase
from ..models import *
from django.contrib.auth.models import User
from ..views import *
from users.models import Profile
from users.models import *


class TeamModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Fra = Team.objects.create(team_name='Frankreich',
                                  team_ccode='FRA', win_points=20, eliminated=False)
        Ger = Team.objects.create(team_name='Deutschland',
                                  team_ccode='GER', win_points=20, eliminated=False)
        Esp = Team.objects.create(team_name='Spanien',
                                  team_ccode='ESP', win_points=20, eliminated=False)
        Ita = Team.objects.create(team_name='Italien',
                                  team_ccode='ITA', win_points=20, eliminated=False)
        Ned = Team.objects.create(team_name='Holland',
                                  team_ccode='NED', win_points=20, eliminated=False)
        Eng = Team.objects.create(team_name='England',
                                  team_ccode='ENG', win_points=20, eliminated=False)

        Ger_Fra = Match.objects.create(
            home_team=Ger, guest_team=Fra, home_score=1, guest_score=2, matchday=3)
        Ger_Esp = Match.objects.create(
            home_team=Ger, guest_team=Esp, home_score=1, guest_score=2, matchday=3)
        Ger_Ita = Match.objects.create(
            home_team=Ger, guest_team=Ita, home_score=1, guest_score=2, matchday=3)
        Ger_Ned = Match.objects.create(
            home_team=Ger, guest_team=Ned, home_score=1, guest_score=2, matchday=3)
        Ger_Eng = Match.objects.create(
            home_team=Ger, guest_team=Eng, home_score=1, guest_score=2, matchday=3)
        # ---------
        Fra_Ita = Match.objects.create(
            home_team=Fra, guest_team=Ita, home_score=1, guest_score=2, matchday=5)
        Fra_Esp = Match.objects.create(
            home_team=Fra, guest_team=Esp, home_score=1, guest_score=2, matchday=5)
        Fra_Ned = Match.objects.create(
            home_team=Fra, guest_team=Ned, home_score=1, guest_score=2, matchday=5)
        Fra_Eng = Match.objects.create(
            home_team=Fra, guest_team=Eng, home_score=1, guest_score=2, matchday=5)
        # ---------
        Esp_Ita = Match.objects.create(
            home_team=Esp, guest_team=Ita, home_score=1, guest_score=2)
        Esp_Ned = Match.objects.create(
            home_team=Esp, guest_team=Ned, home_score=1, guest_score=2)
        Esp_Eng = Match.objects.create(
            home_team=Esp, guest_team=Eng, home_score=1, guest_score=2)
        # ---------
        Ita_Ned = Match.objects.create(
            home_team=Ita, guest_team=Ned, home_score=1, guest_score=2)
        Ita_Eng = Match.objects.create(
            home_team=Ita, guest_team=Eng, home_score=1, guest_score=2)
        # ---------
        Ned_Eng = Match.objects.create(
            home_team=Ned, guest_team=Eng, home_score=1, guest_score=2)

        Boris_Yelzin = User.objects.create(
            username='boris_yelzin', email='b.yelzin@kremlin.ru', is_staff=False, is_active=True, date_joined=datetime.now())
        Silvio_Berlusconi = User.objects.create(
            username='silvio_berlusconi', email='s.berlusconi@rome.it', is_staff=False, is_active=True, date_joined=datetime.now())
        Johann_Kaeskopp = User.objects.create(
            username='johann_kaeskopp', email='j.kaeskopp@amstel.nd', is_staff=False, is_active=True, date_joined=datetime.now())
        Angela_Merkel = User.objects.create(
            username='angela_merkel', email='a.merkel@brd.de', is_staff=False, is_active=True, date_joined=datetime.now())
        King_Felippe = User.objects.create(
            username='king_felippe', email='k.felippe@real.es', is_staff=False, is_active=True, date_joined=datetime.now())
        John_Doe = User.objects.create(
            username='john_doe', email='j.doe@ordinary.com', is_staff=False, is_active=True, date_joined=datetime.now())

        Profile_Boris_Yelzin = User.objects.get(
            username='boris_yelzin').profile
        Profile_Silvio_Berlusconi = User.objects.get(
            username='silvio_berlusconi').profile
        Profile_Johann_Kaeskopp = User.objects.get(
            username='johann_kaeskopp').profile
        Profile_Angela_Merkel = User.objects.get(
            username='angela_merkel').profile
        Profile_King_Felippe = User.objects.get(
            username='king_felippe').profile
        Profile_John_Doe = User.objects.get(username='john_doe').profile

        tip1_boris = Tip.objects.create(
            author=Boris_Yelzin, match=Ger_Fra, tip_home=0, tip_guest=0, joker=False)
        tip2_boris = Tip.objects.create(
            author=Boris_Yelzin, match=Ger_Esp, tip_home=0, tip_guest=1, joker=False)
        tip3_boris = Tip.objects.create(
            author=Boris_Yelzin, match=Ger_Ita, tip_home=1, tip_guest=2, joker=True)
        tip4_boris = Tip.objects.create(
            author=Boris_Yelzin, match=Ger_Eng, tip_home=0, tip_guest=1, joker=False)
        tip5_boris = Tip.objects.create(
            author=Boris_Yelzin, match=Ger_Ned, tip_home=1, tip_guest=1, joker=False)
        # ---------------
        tip1_silvio = Tip.objects.create(
            author=Silvio_Berlusconi, match=Ger_Fra, tip_home=1, tip_guest=0, joker=False)
        tip2_silvio = Tip.objects.create(
            author=Silvio_Berlusconi, match=Ger_Esp, tip_home=0, tip_guest=1, joker=False)
        tip3_silvio = Tip.objects.create(
            author=Silvio_Berlusconi, match=Ger_Ita, tip_home=2, tip_guest=0, joker=False)
        tip4_silvio = Tip.objects.create(
            author=Silvio_Berlusconi, match=Ger_Eng, tip_home=0, tip_guest=1, joker=False)
        tip5_silvio = Tip.objects.create(
            author=Silvio_Berlusconi, match=Ger_Ned, tip_home=5, tip_guest=1, joker=True)
        # ---------------
        tip1_johann = Tip.objects.create(
            author=Johann_Kaeskopp, match=Ger_Fra, tip_home=3, tip_guest=0, joker=True)
        tip2_johann = Tip.objects.create(
            author=Johann_Kaeskopp, match=Ger_Esp, tip_home=1, tip_guest=1, joker=False)
        tip3_johann = Tip.objects.create(
            author=Johann_Kaeskopp, match=Ger_Ita, tip_home=3, tip_guest=0, joker=False)
        tip4_johann = Tip.objects.create(
            author=Johann_Kaeskopp, match=Ger_Eng, tip_home=1, tip_guest=1, joker=False)
        tip5_johann = Tip.objects.create(
            author=Johann_Kaeskopp, match=Ger_Ned, tip_home=0, tip_guest=1, joker=False)
        # ---------------
        tip1_angela = Tip.objects.create(
            author=Angela_Merkel, match=Ger_Fra, tip_home=2, tip_guest=2, joker=False)
        tip2_angela = Tip.objects.create(
            author=Angela_Merkel, match=Ger_Esp, tip_home=1, tip_guest=4, joker=True)
        tip3_angela = Tip.objects.create(
            author=Angela_Merkel, match=Ger_Ita, tip_home=3, tip_guest=4, joker=False)
        tip4_angela = Tip.objects.create(
            author=Angela_Merkel, match=Ger_Eng, tip_home=1, tip_guest=4, joker=False)
        tip5_angela = Tip.objects.create(
            author=Angela_Merkel, match=Ger_Ned, tip_home=0, tip_guest=0, joker=False)
        tip6_angela = Tip.objects.create(author=Angela_Merkel, match=Fra_Ita, tip_home=2, tip_guest=1, joker=True)
        tip7_angela = Tip.objects.create(author=Angela_Merkel, match=Fra_Esp, tip_home=2, tip_guest=1, joker=False)
        tip8_angela = Tip.objects.create(author=Angela_Merkel, match=Fra_Ned, tip_home=2, tip_guest=1, joker=False)
        # ---------------
        tip1_felippe = Tip.objects.create(
            author=King_Felippe, match=Ger_Fra, tip_home=2, tip_guest=3, joker=False)
        tip2_felippe = Tip.objects.create(
            author=King_Felippe, match=Ger_Esp, tip_home=2, tip_guest=1, joker=False)
        tip3_felippe = Tip.objects.create(
            author=King_Felippe, match=Ger_Ita, tip_home=0, tip_guest=1, joker=False)
        tip4_felippe = Tip.objects.create(
            author=King_Felippe, match=Ger_Eng, tip_home=1, tip_guest=4, joker=True)
        tip5_felippe = Tip.objects.create(
            author=King_Felippe, match=Ger_Ned, tip_home=3, tip_guest=3, joker=False)

    def test_tip_points_endround_multiplier(self):
        match_1 = Match.objects.get(
            home_team__team_name='Deutschland', guest_team__team_name='Italien', matchday=3)
        tip_1 = Tip.objects.get(
            match=match_1, author__username='angela_merkel')
        match_1.home_score = 3
        match_1.guest_score = 4
        match_1.save()
        self.assertEqual(tip_1.points(), 12)
        #--------
        match_2 = Match.objects.get(
            home_team__team_name='Frankreich', guest_team__team_name='Italien', matchday=5)
        match_2.home_score = 2
        match_2.guest_score = 1
        match_2.save()
        tip_2 = Tip.objects.get(
            match=match_2, author__username='angela_merkel')
        self.assertEqual(tip_2.points(), 36)
    
    def test_joker_valid_quarter_finals_round_of_sixty(self):
        match = Match.objects.get(
            home_team__team_name='Deutschland', guest_team__team_name='Italien')
        match_ger_fr = Match.objects.get(
            home_team__team_name='Deutschland', guest_team__team_name='Frankreich')
        match_ger_ned = Match.objects.get(
            home_team__team_name='Deutschland', guest_team__team_name='Holland')
        tip = Tip.objects.get(match=match, author__username='angela_merkel')
        user = User.objects.get(username='angela_merkel')
        self.assertEqual(get_n_joker(user=user, matchday_number=3), 1)
        tip = Tip.objects.get(match=match_ger_fr, author__username='angela_merkel')
        tip.joker = True
        tip.save()
        #----------
        self.assertEqual(get_n_joker(user=user, matchday_number=3), 2)
        tip = Tip.objects.get(match=match_ger_ned, author__username='angela_merkel')
        tip.joker = True
        tip.save()
        #----------
        is_joker_valid(matchday_number=3, njoker=get_n_joker(
            user=user, matchday_number=3), tip=tip)
        self.assertEqual(tip.joker, False)
        

    def test_joker_valid_semi_finals_final(self):
        match = Match.objects.get(
            home_team__team_name='Frankreich', guest_team__team_name='Italien')
        match_fr_esp = Match.objects.get(
            home_team__team_name='Frankreich', guest_team__team_name='Spanien')
        match_fr_ned = Match.objects.get(
            home_team__team_name='Frankreich', guest_team__team_name='Holland')
        tip = Tip.objects.get(match=match, author__username='angela_merkel')
        user = User.objects.get(username='angela_merkel')
        self.assertEqual(get_n_joker(user=user, matchday_number=5), 1)
        tip = Tip.objects.get(match=match_fr_esp, author__username='angela_merkel')
        tip.joker = True
        tip.save()
        #----------
        self.assertEqual(get_n_joker(user=user, matchday_number=5), 2)
        tip = Tip.objects.get(match=match_fr_ned, author__username='angela_merkel')
        tip.joker = True
        tip.save()
        #----------
        is_joker_valid(matchday_number=5, njoker=get_n_joker(
            user=user, matchday_number=5), tip=tip)
        self.assertEqual(tip.joker, False)

    def test_ranking(self):
        profiles = Profile.objects.all()

        for profile in profiles:
            profile.update_score_and_joker()
            profile.save()

        # wird in ranking angewendet
        users_ranked = Profile.objects.order_by(
            '-score', '-right_tips', 'joker', 'user__username')
        for user in users_ranked:
            print(user.user.username, user.score, user.joker )
        self.assertEqual(users_ranked[0].user.username, 'boris_yelzin')
        self.assertEqual(users_ranked[5].user.username, 'john_doe')
        self.assertEqual(users_ranked[1].user.username, 'king_felippe')