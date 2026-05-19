from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(
            user=instance,
            defaults={"nombre_completo": instance.get_full_name() or instance.username},
        )
