import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.urls import reverse


class ProfessionalUserManager(BaseUserManager):
    """
    Manager personalizado para o modelo ProfessionalUser.
    """

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Cria e salva um usuário com o email e senha fornecidos.
        """
        if not email:
            raise ValueError("O campo email é obrigatório")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Cria e salva um superusuário com o email e senha fornecidos.
        """
        extra_fields.setdefault('is_tech', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_tech') is not True:
            raise ValueError('Superuser must have is_tech=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)

    def create_staff(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Cria e salva um usuário da equipe (staff/técnico).
        """
        extra_fields.setdefault('is_tech', True)

        if extra_fields.get('is_tech') is not True:
            raise ValueError('Staff must have is_tech=True.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class ProfessionalUser(AbstractBaseUser):
    """
    Modelo de usuário personalizado para o SISInfo V2.
    
    Este modelo substitui o usuário padrão do Django e adiciona
    campos específicos para gestão de profissionais da TI municipal.
    
    Attributes:
        email: Email do usuário (identificador único)
        first_name: Primeiro nome do usuário
        last_name: Sobrenome do usuário
        registration: Número de matrícula funcional (opcional)
        is_tech: Indica se possui privilégios de técnico
        is_admin: Indica se possui privilégios de administrador
        first_login: Indica se ainda não completou onboarding
    """
    first_name = models.CharField('primeiro nome', max_length=100)
    last_name = models.CharField('ultimo nome', max_length=150)
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["is_admin", "is_tech", "first_name"]
        verbose_name = "profissional"
        verbose_name_plural = "profissionais"

    def get_absolute_url(self):
        return reverse('authenticate:profile_user', kwargs={'slug': self.slug})

    def __str__(self):
        if self.registration is None:
            return self.fullname
        return f'{self.fullname} - Matrícula: {self.registration}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = uuid.uuid4()
        return super().save(*args, **kwargs)

    def officer(self):
        """Retorna o cargo do usuário baseado em suas permissões."""
        if self.is_tech is False and self.is_admin is False:
            return 'Estagiário de Suporte em Informática'
        elif self.is_tech is True and self.is_admin is False:
            return 'Técnico de Suporte em Informática'
        elif self.is_tech is True and self.is_admin is True:
            return 'Administrador'

    def has_perm(self, perm, obj=None):
        "O usuário tem permissão específica?"
        # Apenas administradores têm todas as permissões.
        return self.is_admin

    def has_module_perms(self, app_label):
        "O usuário tem permissão para visualizar o app `app_label`?"
        # Apenas administradores têm acesso a todos os módulos.
        return self.is_admin

    @property
    def fullname(self):
        """Retorna nome completo do usuário."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        """Indica se usuário é técnico (compatibilidade Django admin)."""
        return self.is_tech

    @property
    def is_superuser(self):
        """Indica se usuário é administrador (compatibilidade Django admin)."""
        return self.is_admin
    
    def can_access_admin(self) -> bool:
        """
        Verifica se usuário pode acessar painel administrativo.
        
        Returns:
            bool: True se usuário está ativo e é administrador
        """
        return self.is_active and self.is_admin
    
    def get_role_display(self) -> str:
        """
        Retorna nome amigável do cargo do usuário.
        
        Returns:
            str: Nome do cargo baseado em permissões
        """
        return self.officer()
