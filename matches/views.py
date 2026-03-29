from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import UpdateView

from .models import Match
from .forms import MatchResultForm
from championships.services import advance_winner


class MatchUpdateView(UpdateView):
    model = Match
    form_class = MatchResultForm
    template_name = 'matches/form.html'
    context_object_name = 'match'

    def get_success_url(self):
        match = self.object
        if match.group_id:
            return reverse('championships:groups', kwargs={'pk': match.championship_id})
        return reverse('championships:bracket', kwargs={'pk': match.championship_id})

    def form_valid(self, form):
        response = super().form_valid(form)
        match = self.object
        if match.status == 'finalizada':
            advance_winner(match)
            messages.success(self.request, 'Resultado registrado.')
        return response
