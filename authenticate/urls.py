from django.contrib.auth import views as auth_views
from django.urls import path

from authenticate import views

app_name = 'authenticated'

urlpatterns = [
    path('', views.show_users, name='show_users'),
    # path('cadastro_usuario/', views.cadastro_usuario, name="cadastro_usuario"),
    # # Habilitar usuarios
    # path('disable_usuario/<slug:slug>',
    #      views.disable_usuario, name="disable_usuario"),
    # path('enable_usuario/<slug:slug>',
    #      views.enable_usuario, name="enable_usuario"),
    # path('disable_usuario_tech/<slug:slug>',
    #      views.disable_usuario_tech, name="disable_usuario_tech"),
    # path('enable_usuario_tech/<slug:slug>',
    #      views.enable_usuario_tech, name="enable_usuario_tech"),
    # path('disable_usuario_admin/<slug:slug>',
    #      views.disable_usuario_admin, name="disable_usuario_admin"),
    # path('enable_usuario_admin/<slug:slug>',
    #      views.enable_usuario_admin, name="enable_usuario_admin"),
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
