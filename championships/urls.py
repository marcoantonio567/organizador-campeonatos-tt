from django.urls import path
from . import views

app_name = 'championships'

urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='list'),
    path('novo/', views.ChampionshipCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ChampionshipDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.ChampionshipUpdateView.as_view(), name='update'),
    path('<int:pk>/excluir/', views.ChampionshipDeleteView.as_view(), name='delete'),
    path('<int:pk>/inscrever/', views.EnrollPlayerView.as_view(), name='enroll'),
    path('<int:pk>/remover-inscricao/<int:enrollment_pk>/', views.RemoveEnrollmentView.as_view(), name='remove_enrollment'),
    path('<int:pk>/gerar-grupos/', views.GenerateGroupsView.as_view(), name='generate_groups'),
    path('<int:pk>/grupos/', views.GroupsView.as_view(), name='groups'),
    path('<int:pk>/gerar-chave/', views.GenerateEliminationView.as_view(), name='generate_elimination'),
    path('<int:pk>/chave/', views.BracketView.as_view(), name='bracket'),
]
