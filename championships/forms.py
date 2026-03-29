from django import forms
from .models import Championship, Enrollment
from players.models import Player


class ChampionshipForm(forms.ModelForm):
    class Meta:
        model = Championship
        fields = ['name', 'data_inicio', 'data_fim', 'local', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class EnrollPlayerForm(forms.Form):
    player = forms.ModelChoiceField(
        queryset=Player.objects.none(),
        label='Jogador',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, championship, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enrolled_ids = Enrollment.objects.filter(
            championship=championship
        ).values_list('player_id', flat=True)
        self.fields['player'].queryset = Player.objects.exclude(id__in=enrolled_ids)


class GenerateGroupsForm(forms.Form):
    num_groups = forms.IntegerField(
        label='Número de grupos',
        min_value=2,
        max_value=16,
        initial=4,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
