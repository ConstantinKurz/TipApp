from django.db import models
from django.contrib.auth.models import User
from tip_app_main.models import Team, Tip

for i in range(10):
    user = User.objects.create_user('testuser' + i, 'constantin.kurz@aol.com', 'testCredential' + i)