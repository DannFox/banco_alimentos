from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import PerfilUsuario, Rol


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ("rol", "nombre_completo", "rol_display")

    rol_display = serializers.CharField(source="get_rol_display", read_only=True)


class UserSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "perfil")


class RegistroSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    nombre_completo = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ese nombre de usuario ya existe.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email") or "",
            password=validated_data["password"],
        )
        nombre = validated_data.get("nombre_completo") or validated_data["username"]
        perfil = user.perfil
        perfil.nombre_completo = nombre
        perfil.rol = Rol.VOLUNTARIO
        perfil.save()
        return user
