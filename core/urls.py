from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', RedirectView.as_view(url='/campeonatos/', permanent=False)),
    path('jogadores/', include('players.urls', namespace='players')),
    path('campeonatos/', include('championships.urls', namespace='championships')),
    path('partidas/', include('matches.urls', namespace='matches')),
    path('gerenciar-admins/', include('core.admin_urls', namespace='admins')),
]
