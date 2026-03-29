from django import forms
from .models import Player, PlayerCategoryRanking, CATEGORY_CHOICES


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PlayerCategoryRankingForm(forms.Form):
    pontos_iniciante = forms.IntegerField(
        label='Pontos — Iniciante',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Deixe vazio para não cadastrar nessa categoria',
        }),
    )
    pontos_intermediario = forms.IntegerField(
        label='Pontos — Intermediário',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Deixe vazio para não cadastrar nessa categoria',
        }),
    )
    pontos_avancado = forms.IntegerField(
        label='Pontos — Avançado',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Deixe vazio para não cadastrar nessa categoria',
        }),
    )
