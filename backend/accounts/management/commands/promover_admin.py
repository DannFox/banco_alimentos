from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import PerfilUsuario, Rol


class Command(BaseCommand):
    help = "Asigna rol administrador a un usuario existente (ej. el superusuario)."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No existe el usuario: {username}"))
            return
        p, _ = PerfilUsuario.objects.get_or_create(
            user=u,
            defaults={"nombre_completo": u.get_full_name() or u.username, "rol": Rol.VOLUNTARIO},
        )
        p.rol = Rol.ADMINISTRADOR
        p.save()
        self.stdout.write(self.style.SUCCESS(f"{username} ahora es administrador."))
