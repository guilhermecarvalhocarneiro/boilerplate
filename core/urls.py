from django.urls import path

from nuvols.core.views import (IndexAdminTemplateView, LoginView, ProfileView, ProfileUpdateView,
                               UpdatePassword, ResetPassword, SettingsView)

app_name = 'core'
urlpatterns = [
    path('', IndexAdminTemplateView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/reset/password/', ResetPassword.as_view(), name='reset-password'),
    path('profile/update/password/', UpdatePassword.as_view(), name='password-update'),
    path('settings/', SettingsView.as_view(), name='settings'),
]
