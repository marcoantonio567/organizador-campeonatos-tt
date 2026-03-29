from django import forms
from .models import Match


class MatchResultForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['score_a', 'score_b', 'status']
        widgets = {
            'score_a': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'score_b': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
