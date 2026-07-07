from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class UserRole(models.TextChoices):
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
    RECECIONISTA = "RECECIONISTA", "Rececionista"
    MEDICO = "MEDICO", "Médico"
    ENFERMEIRO = "ENFERMEIRO", "Enfermeiro"
    LABORATORIO = "LABORATORIO", "Laboratório"
    FINANCEIRO = "FINANCEIRO", "Financeiro"
    DIRECTOR = "DIRECTOR", "Director"


class Gender(models.TextChoices):
    MASCULINO = "M", "Masculino"
    FEMININO = "F", "Feminino"
    OUTRO = "O", "Outro"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("E-mail", unique=True)
    first_name = models.CharField("Nome", max_length=150)
    last_name = models.CharField("Apelido", max_length=150)
    phone = models.CharField("Telefone", max_length=20, blank=True)
    gender = models.CharField(
        "Sexo",
        max_length=1,
        choices=Gender.choices,
        blank=True,
    )
    birth_date = models.DateField("Data de nascimento", null=True, blank=True)
    position = models.CharField("Cargo", max_length=150, blank=True)
    photo = models.ImageField("Fotografia", upload_to="users/photos/", blank=True, null=True)
    role = models.CharField(
        "Perfil",
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.RECECIONISTA,
    )
    is_active = models.BooleanField("Ativo", default=True)
    is_staff = models.BooleanField("Acesso ao admin", default=False)
    date_joined = models.DateTimeField("Data de registo", default=timezone.now)
    last_login = models.DateTimeField("Último acesso", blank=True, null=True)
    last_activity = models.DateTimeField("Última atividade", blank=True, null=True)
    deleted_at = models.DateTimeField("Eliminado em", blank=True, null=True)

    objects = UserManager()
    all_objects = models.Manager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return self.get_full_name() or self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        return self.first_name

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["deleted_at", "is_active"])

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save(update_fields=["deleted_at", "is_active"])
