from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Rol
from .permissions import EsAdministrador, rol_usuario
from .serializers import RegistroSerializer, UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        perfil = getattr(user, "perfil", None)
        token["rol"] = perfil.rol if perfil else Rol.VOLUNTARIO
        token["nombre"] = perfil.nombre_completo if perfil else user.username
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(
            {"mensaje": "Usuario creado. Rol asignado: Voluntario.", "username": user.username},
            status=status.HTTP_201_CREATED,
        )


class PerfilActualView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class CambiarRolView(APIView):
    permission_classes = (EsAdministrador,)

    def post(self, request):
        from django.contrib.auth.models import User

        username = request.data.get("username")
        nuevo_rol = request.data.get("rol")
        if not username or nuevo_rol not in dict(Rol.choices):
            return Response(
                {"error": "Se requiere username y rol válido (administrador, coordinador, voluntario)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        perfil = u.perfil
        perfil.rol = nuevo_rol
        perfil.save()
        return Response(UserSerializer(u).data)


class ListaUsuariosView(APIView):
    permission_classes = (EsAdministrador,)

    def get(self, request):
        from django.contrib.auth.models import User

        users = User.objects.select_related("perfil").all()
        return Response(UserSerializer(users, many=True).data)
