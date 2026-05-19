from rest_framework import permissions

from .models import Rol


def rol_usuario(user):
    if not user.is_authenticated:
        return None
    perfil = getattr(user, "perfil", None)
    return perfil.rol if perfil else None


class EsAdministrador(permissions.BasePermission):
    def has_permission(self, request, view):
        return rol_usuario(request.user) == Rol.ADMINISTRADOR


class PuedeGestionarInventario(permissions.BasePermission):
    """Administrador y coordinador: CRUD productos, movimientos, exportar."""

    def has_permission(self, request, view):
        r = rol_usuario(request.user)
        return r in (Rol.ADMINISTRADOR, Rol.COORDINADOR)


class PuedeRegistrarMovimientos(permissions.BasePermission):
    """Voluntario puede registrar entradas/salidas y consultar."""

    def has_permission(self, request, view):
        r = rol_usuario(request.user)
        return r in (Rol.ADMINISTRADOR, Rol.COORDINADOR, Rol.VOLUNTARIO)


class PuedeExportarRegistro(permissions.BasePermission):
    def has_permission(self, request, view):
        r = rol_usuario(request.user)
        return r in (Rol.ADMINISTRADOR, Rol.COORDINADOR)
