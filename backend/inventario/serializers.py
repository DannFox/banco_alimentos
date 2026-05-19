from django.utils import timezone
from rest_framework import serializers

from .models import Movimiento, Producto, TipoMovimiento


class ProductoSerializer(serializers.ModelSerializer):
    dias_para_vencer = serializers.SerializerMethodField()
    alerta_caducidad = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = (
            "id",
            "nombre",
            "codigo_barras",
            "cantidad",
            "fecha_vencimiento",
            "dias_para_vencer",
            "alerta_caducidad",
            "creado_en",
            "actualizado_en",
        )
        read_only_fields = ("creado_en", "actualizado_en")

    def get_dias_para_vencer(self, obj):
        return (obj.fecha_vencimiento - timezone.localdate()).days

    def get_alerta_caducidad(self, obj):
        dias = self.get_dias_para_vencer(obj)
        return dias <= 7 and obj.cantidad > 0


class MovimientoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = Movimiento
        fields = (
            "id",
            "producto",
            "producto_nombre",
            "tipo",
            "cantidad",
            "nota",
            "registrado_en",
            "usuario",
            "usuario_username",
        )
        read_only_fields = ("registrado_en", "usuario", "usuario_username")

    def validate(self, attrs):
        tipo = attrs.get("tipo")
        cantidad = attrs.get("cantidad")
        producto = attrs.get("producto")
        if tipo == TipoMovimiento.SALIDA and producto and cantidad:
            if producto.cantidad < cantidad:
                raise serializers.ValidationError(
                    {"cantidad": f"Stock insuficiente. Disponible: {producto.cantidad}."}
                )
        return attrs


class MovimientoCreateSerializer(MovimientoSerializer):
    def create(self, validated_data):
        request = self.context["request"]
        mov = Movimiento.objects.create(usuario=request.user, **validated_data)
        p = mov.producto
        if mov.tipo == TipoMovimiento.ENTRADA:
            p.cantidad += mov.cantidad
        else:
            p.cantidad -= mov.cantidad
        p.save()
        return mov


class BusquedaRapidaSerializer(serializers.Serializer):
    """Consulta por código de barras usando índice hash en memoria."""

    codigo_barras = serializers.CharField(max_length=64)


def _dias_vencer(obj: Producto) -> int:
    return (obj.fecha_vencimiento - timezone.localdate()).days


def urgencia_publica(obj: Producto) -> str:
    dias = _dias_vencer(obj)
    if obj.cantidad <= 0:
        return "SIN_STOCK"
    if dias < 0:
        return "VENCIDO"
    if dias <= 3:
        return "CRÍTICO"
    if dias <= 7:
        return "URGENTE"
    if dias <= 14:
        return "PRÓXIMO"
    return "NORMAL"


class ProductoPublicoEstructurasSerializer(serializers.ModelSerializer):
    """Solo lectura pública para la página de estructuras (sin token)."""

    dias_para_vencer = serializers.SerializerMethodField()
    urgencia = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ("id", "nombre", "fecha_vencimiento", "cantidad", "dias_para_vencer", "urgencia")

    def get_dias_para_vencer(self, obj: Producto) -> int:
        return _dias_vencer(obj)

    def get_urgencia(self, obj: Producto) -> str:
        return urgencia_publica(obj)
