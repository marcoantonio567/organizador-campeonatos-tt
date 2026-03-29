from django.urls import path
from .views import AdminListView, AdminCreateView, AdminDeleteView

app_name = 'admins'

urlpatterns = [
    path('', AdminListView.as_view(), name='list'),
    path('novo/', AdminCreateView.as_view(), name='create'),
    path('<int:pk>/excluir/', AdminDeleteView.as_view(), name='delete'),
]
