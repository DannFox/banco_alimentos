from django.conf import settings
from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    codigo_barras = models.CharField(max_length=64, blank=True, db_index=True)
    cantidad = models.PositiveIntegerField(default=0)
    fecha_vencimiento = models.DateField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha_vencimiento", "nombre"]
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} ({self.cantidad})"


class TipoMovimiento(models.TextChoices):
    ENTRADA = "entrada", "Entrada"
    SALIDA = "salida", "Salida"


class Movimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=16, choices=TipoMovimiento.choices)
    cantidad = models.PositiveIntegerField()
    nota = models.CharField(max_length=500, blank=True)
    registrado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="movimientos_inventario",
    )

    class Meta:
        ordering = ["-registrado_en"]
        verbose_name_plural = "Movimientos"
