from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('<int:pk>/resultado/', views.MatchUpdateView.as_view(), name='update'),
]
