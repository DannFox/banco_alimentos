from django.contrib import admin

from .models import Movimiento, Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo_barras", "cantidad", "fecha_vencimiento")
    search_fields = ("nombre", "codigo_barras")


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ("producto", "tipo", "cantidad", "usuario", "registrado_en")
    list_filter = ("tipo",)
