from django.contrib import admin
from .models import Tip
from .models import Match
from .models import Team

admin.site.register(Tip)
admin.site.register(Match)
admin.site.register(Team)