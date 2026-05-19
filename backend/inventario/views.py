from datetime import timedelta

from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from accounts.permissions import PuedeExportarRegistro, PuedeGestionarInventario, PuedeRegistrarMovimientos

from .exportacion import generar_excel_registro, generar_pdf_registro
from .models import Movimiento, Producto, TipoMovimiento
from .serializers import (
    BusquedaRapidaSerializer,
    MovimientoCreateSerializer,
    MovimientoSerializer,
    ProductoPublicoEstructurasSerializer,
    ProductoSerializer,
)
from .services.hash_index import buscar_por_codigo_barras, construir_indice_productos
from .services.hash_stats import computar_estadisticas_hash
from .services.priority_queue import construir_cola_prioridad, extraer_orden_salida


class ProductoListaCrearView(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [PuedeRegistrarMovimientos()]
        return [PuedeGestionarInventario()]

    def perform_create(self, serializer):
        serializer.save()


class ProductoDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [PuedeRegistrarMovimientos()]
        return [PuedeGestionarInventario()]


class MovimientoListaCrearView(generics.ListCreateAPIView):
    queryset = Movimiento.objects.select_related("producto", "usuario").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MovimientoCreateSerializer
        return MovimientoSerializer

    def get_permissions(self):
        return [PuedeRegistrarMovimientos()]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        with transaction.atomic():
            obj = ser.save()
        return Response(MovimientoSerializer(obj).data, status=status.HTTP_201_CREATED)


class ColaPrioridadView(views.APIView):
    """Productos con stock ordenados por vencimiento (estructura: cola de prioridad)."""

    def get_permissions(self):
        return [PuedeRegistrarMovimientos()]

    def get(self, request):
        qs = Producto.objects.filter(cantidad__gt=0)
        heap = construir_cola_prioridad(qs)
        orden = extraer_orden_salida(heap)
        return Response(ProductoSerializer(orden, many=True).data)


class AlertasView(views.APIView):
    """Productos que caducan en 7 días o menos (con stock)."""

    def get_permissions(self):
        return [PuedeRegistrarMovimientos()]

    def get(self, request):
        hoy = timezone.localdate()
        limite = hoy + timedelta(days=7)
        qs = Producto.objects.filter(
            cantidad__gt=0,
            fecha_vencimiento__lte=limite,
        ).order_by("fecha_vencimiento")
        return Response(ProductoSerializer(qs, many=True).data)


class BusquedaCodigoView(views.APIView):
    def get_permissions(self):
        return [PuedeRegistrarMovimientos()]

    def post(self, request):
        ser = BusquedaRapidaSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        codigo = ser.validated_data["codigo_barras"]
        qs = Producto.objects.all()
        idx = construir_indice_productos(qs)
        p = buscar_por_codigo_barras(idx, codigo)
        if not p:
            return Response({"encontrado": False, "mensaje": "Código no registrado."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"encontrado": True, "producto": ProductoSerializer(p).data})


class DashboardResumenView(views.APIView):
    def get_permissions(self):
        return [PuedeRegistrarMovimientos()]

    def get(self, request):
        total_productos = Producto.objects.count()
        con_stock = Producto.objects.filter(cantidad__gt=0).count()
        hoy = timezone.localdate()
        alertas = Producto.objects.filter(
            cantidad__gt=0,
            fecha_vencimiento__lte=hoy + timedelta(days=7),
        ).count()
        return Response(
            {
                "total_productos": total_productos,
                "productos_con_stock": con_stock,
                "alertas_proximas": alertas,
            }
        )


class ExportarExcelView(views.APIView):
    permission_classes = [PuedeExportarRegistro]

    def get(self, request):
        data = generar_excel_registro()
        resp = HttpResponse(
            data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        fname = f"registro_banco_alimentos_{timezone.localdate().isoformat()}.xlsx"
        resp["Content-Disposition"] = f'attachment; filename="{fname}"'
        return resp


class ExportarPdfView(views.APIView):
    permission_classes = [PuedeExportarRegistro]

    def get(self, request):
        data = generar_pdf_registro()
        resp = HttpResponse(data, content_type="application/pdf")
        fname = f"registro_banco_alimentos_{timezone.localdate().isoformat()}.pdf"
        resp["Content-Disposition"] = f'attachment; filename="{fname}"'
        return resp


class EstructurasDatosPublicoView(views.APIView):
    """
    Datos reales del inventario para la página pública de estructuras (solo lectura).
    Cola de prioridad: productos con stock ordenados por vencimiento (heap).
    Hash: estadísticas derivadas del mismo catálogo que alimenta el índice dict.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes: list = []

    def get(self, request):
        qs_stock = Producto.objects.filter(cantidad__gt=0)
        heap = construir_cola_prioridad(qs_stock)
        orden = extraer_orden_salida(heap)
        cola_data = ProductoPublicoEstructurasSerializer(orden, many=True).data

        catalogo = list(Producto.objects.all())
        hash_data = computar_estadisticas_hash(catalogo)

        return Response(
            {
                "cola_prioridad": {
                    "total_en_heap": len(cola_data),
                    "orden": cola_data,
                    "raiz": cola_data[0] if cola_data else None,
                    "top": cola_data[:5],
                },
                "tabla_hash": hash_data,
                "actualizado_en": timezone.now().isoformat(),
            }
        )
