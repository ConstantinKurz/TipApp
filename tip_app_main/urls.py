from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='tip-home'),
    path('tips_per_matchday/<int:matchday_number>/', views.tip_matchday, name='tip-matchday'),
    path('ranking/', views.ranking, name='tip-ranking'),
    path('results_per_day/<int:matchday_number>/', views.results, name='tip-results'),
    path('email/', views.email, name='tip-mail'),
    path('email/reminder', views.reminder_email, name='tip-reminder-mail'),
    path('email/reminder/<int:matchday>/', views.reminder_email, name='tip-reminder-mail'),
    path('view-pdf/', views.pdf_view,name='pdf-view'),
    path('export-csv/', views.csv_export, name='export-csv'),
    ]

