from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView


class AdminUserForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'tt-form-control'}),
    )
    password_confirm = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'class': 'tt-form-control'}),
    )

    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'tt-form-control'}),
        }
        labels = {
            'username': 'Usuário',
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'As senhas não coincidem.')
        return cleaned


class AdminListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'admins/list.html'
    context_object_name = 'admins'

    def get_queryset(self):
        return User.objects.all().order_by('username')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = AdminUserForm()
        return ctx


class AdminCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = AdminUserForm
    success_url = reverse_lazy('admins:list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_staff = True
        user.save()
        messages.success(self.request, f'Admin "{user.username}" criado com sucesso.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return redirect('admins:list')


class AdminDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('admins:list')

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            messages.error(request, 'Você não pode excluir sua própria conta.')
            return redirect('admins:list')
        username = user.username
        user.delete()
        messages.success(request, f'Admin "{username}" removido.')
        return redirect(self.success_url)
