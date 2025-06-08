from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.conf import settings
from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Вход'}

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('home')

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if 'username' in form.errors:
            form.errors['username'] = ['Пожалуйста, введите правильный email.']
        return response

class LogoutUser(LogoutView):
    next_page = reverse_lazy('users:login')

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')

class ProfileUser(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль'}

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['default_image'] = settings.MEDIA_URL + 'users/default.png'
        return context

    def get_object(self):
        return self.request.user

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change.html'
    extra_context = {'title': 'Изменение пароля'}

class UserPasswordReset(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    extra_context = {'title': 'Восстановление пароля'}

class UserPasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    extra_context = {'title': 'Восстановление пароля'}

class UserPasswordResetDone(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'
    extra_context = {'title': 'Восстановление пароля'}

class UserPasswordResetComplete(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
    extra_context = {'title': 'Восстановление пароля'}