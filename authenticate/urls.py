from django.contrib.auth import views as auth_views
from django.urls import path

from authenticate import views

app_name = 'authenticated'

urlpatterns = [
    path('', views.show_users, name='show_users'),
    # path('cadastro_usuario/', views.cadastro_usuario, name="cadastro_usuario"),
    # Habilitar usuarios
    path('disabled_user/<slug:slug>',
         views.disabled_user, name="disabled_user"),
    path('enabled_user/<slug:slug>',
         views.enabled_user, name="enabled_user"),
    path('disabled_user_tech/<slug:slug>',
         views.disabled_user_tech, name="disabled_user_tech"),
    path('enabled_user_tech/<slug:slug>',
         views.enabled_user_tech, name="enabled_user_tech"),
    path('disabled_user_admin/<slug:slug>',
         views.disabled_user_admin, name="disabled_user_admin"),
    path('enabled_user_admin/<slug:slug>',
         views.enabled_user_admin, name="enabled_user_admin"),
    # Login // Logout
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_page, name="logout"),
    path('change_password/<slug:slug>/',
         views.change_password, name="change_password"),
    # # # Perfil do Usuario
    # path('profile/<slug:slug>', views.change_password, name="usuario"),
    # Redefinir Senha
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name="password_reset.html"), name="password_reset"),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name="password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="password_reset_confirm_view.html"), name="password_reset_confirm"),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="password_reset_complete.html"), name="password_reset_complete"),
]
