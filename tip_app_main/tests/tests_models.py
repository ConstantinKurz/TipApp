from django.test import TestCase
from ..models import *
# Create your tests here.
class TeamModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Team.objects.create(team_name = 'Frankreich', team_ccode = 'FRA', win_points = 20, eliminated = False)

    def test_team_name(self):
        team = Team.objects.get(team_name = 'Frankreich')
        self.assertEqual(team.team_name, 'Frankreich')
        self.assertEqual(team.team_ccode, 'FRA')
        self.assertEqual(team.win_points, 20)
        self.assertEqual(team.eliminated, False)