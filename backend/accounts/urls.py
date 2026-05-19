from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CambiarRolView,
    CustomTokenObtainPairView,
    ListaUsuariosView,
    PerfilActualView,
    RegistroView,
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("registro/", RegistroView.as_view(), name="registro"),
    path("yo/", PerfilActualView.as_view(), name="perfil_actual"),
    path("usuarios/", ListaUsuariosView.as_view(), name="lista_usuarios"),
    path("cambiar-rol/", CambiarRolView.as_view(), name="cambiar_rol"),
]
