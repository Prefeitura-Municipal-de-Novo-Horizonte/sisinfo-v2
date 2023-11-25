import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.shortcuts import resolve_url as r

# Create your models here.


class ProfessionalUserManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, password=None):
        if not email and not username:
            raise ValueError(
                "Já existe um profissional cadastrado com esse email ou username")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, first_name, last_name, password=None):
        user = self.create_user(
            username,
            email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_tech = True
        user.is_admin = True
        user.save(using=self._db)
        return user

    def create_staff(self, username, email, first_name, last_name, password=None):
        user = self.create_user(
            username,
            email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_tech = True
        user.save(using=self._db)
        return user


class ProfessionalUser(AbstractBaseUser):
    first_name = models.CharField('primeiro nome', max_length=100)
    last_name = models.CharField('ultimo nome', max_length=150)
    username = models.CharField('usuario', unique=True,
                                max_length=100, blank=True, null=True)
    registration = models.CharField(
        'numero de matrícula', max_length=8, blank=True, null=True)
    slug = models.SlugField('slug', unique=True, max_length=150)
    email = models.EmailField(
        'email',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField('ativo', default=True)
    is_tech = models.BooleanField('tecnico', default=False)
    is_admin = models.BooleanField('administrador', default=False)
    first_login = models.BooleanField('primeiro login', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    objects = ProfessionalUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    class Meta:
        ordering = ["is_admin", "is_tech", "first_name"]
        verbose_name = "profissional"
        verbose_name_plural = "profissionais"

    def get_absolute_url(self):
        return r('authenticated:profile_user', slug=self.slug)

    def __str__(self):
        if self.registration is None:
            return self.fullname
        return f'{self.fullname} - Matrícula: {self.registration}'

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = uuid.uuid4()
        return super().save()

    def officer(self):
        if self.is_tech is False and self.is_admin is False:
            return 'Estagiário de Suporte em Informática'
        elif self.is_tech is True and self.is_admin is False:
            return 'Técnico de Suporte em Informática'
        elif self.is_tech is True and self.is_admin is True:
            return 'Administrador'

    def has_perm(self, perm, obj=None):
        "O usuário tem permissão específica?"
        # Resposta mais simples possível: Sim, sempre
        return True

    def has_module_perms(self, app_label):
        "O usuário tem permissão para visualizar o app `app_label`?"
        # Resposta mais simples possível: Sim, sempre
        return True

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        "Este usuário é um Tecnico?"
        # Resposta mais simples possível: Todos Administradores são tecnicos
        return self.is_tech

    @property
    def is_superuser(self):
        "Este usuário é um Administrador?"
        # Resposta mais simples possível: somente usuario administrator
        return self.is_admin
