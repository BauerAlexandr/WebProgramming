from django.urls import path
from .views import (
    LoginUser, LogoutUser, RegisterUser, ProfileUser,
    UserPasswordChange, UserPasswordReset, UserPasswordResetConfirm,
    UserPasswordResetDone, UserPasswordResetComplete
)
from django.contrib.auth.views import PasswordChangeDoneView

app_name = 'users'

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('profile/', ProfileUser.as_view(), name='profile'),
    path('password-change/', UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),
    path('password-reset/', UserPasswordReset.as_view(), name='password_reset'),
    path('password-reset/<uidb64>/<token>/', UserPasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password-reset/done/', UserPasswordResetDone.as_view(), name='password_reset_done'),
    path('password-reset/complete/', UserPasswordResetComplete.as_view(), name='password_reset_complete'),
]