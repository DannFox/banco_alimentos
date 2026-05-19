from django.conf import settings
from django.db import models


class Rol(models.TextChoices):
    """Roles del personal del banco (según anteproyecto: usuarios con permisos)."""

    ADMINISTRADOR = "administrador", "Administrador"
    COORDINADOR = "coordinador", "Coordinador de inventario"
    VOLUNTARIO = "voluntario", "Voluntario"


class PerfilUsuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    rol = models.CharField(
        max_length=32,
        choices=Rol.choices,
        default=Rol.VOLUNTARIO,
    )
    nombre_completo = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
