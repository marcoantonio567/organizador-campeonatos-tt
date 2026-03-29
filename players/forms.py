from django import forms
from .models import Player


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'ranking_atual', 'categoria']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ranking_atual': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }
