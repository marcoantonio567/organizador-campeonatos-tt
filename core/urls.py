from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/campeonatos/', permanent=False)),
    path('jogadores/', include('players.urls', namespace='players')),
    path('campeonatos/', include('championships.urls', namespace='championships')),
    path('partidas/', include('matches.urls', namespace='matches')),
]
