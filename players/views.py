from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Player
from .forms import PlayerForm


class PlayerListView(ListView):
    model = Player
    template_name = 'players/list.html'
    context_object_name = 'players'
    ordering = ['-ranking_atual']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx['categories'] = [
            ('avancado',      'Avançado',      qs.filter(categoria='avancado')),
            ('intermediario', 'Intermediário', qs.filter(categoria='intermediario')),
            ('iniciante',     'Iniciante',     qs.filter(categoria='iniciante')),
        ]
        return ctx


class PlayerDetailView(DetailView):
    model = Player
    template_name = 'players/detail.html'
    context_object_name = 'player'


class PlayerCreateView(CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/form.html'
    success_url = reverse_lazy('players:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Novo Jogador'
        return ctx


class PlayerUpdateView(UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/form.html'
    success_url = reverse_lazy('players:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Editar — {self.object.name}'
        return ctx


class PlayerDeleteView(DeleteView):
    model = Player
    template_name = 'players/confirm_delete.html'
    success_url = reverse_lazy('players:list')
    context_object_name = 'player'
