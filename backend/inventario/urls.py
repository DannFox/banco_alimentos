from django.urls import path

from .views import (
    AlertasView,
    BusquedaCodigoView,
    ColaPrioridadView,
    DashboardResumenView,
    EstructurasDatosPublicoView,
    ExportarExcelView,
    ExportarPdfView,
    MovimientoListaCrearView,
    ProductoDetalleView,
    ProductoListaCrearView,
)

urlpatterns = [
    path("publico/estructuras/", EstructurasDatosPublicoView.as_view(), name="estructuras_publico"),
    path("dashboard/", DashboardResumenView.as_view(), name="dashboard"),
    path("productos/", ProductoListaCrearView.as_view(), name="producto_lista"),
    path("productos/<int:pk>/", ProductoDetalleView.as_view(), name="producto_detalle"),
    path("movimientos/", MovimientoListaCrearView.as_view(), name="movimiento_lista"),
    path("cola-prioridad/", ColaPrioridadView.as_view(), name="cola_prioridad"),
    path("alertas/", AlertasView.as_view(), name="alertas"),
    path("buscar-codigo/", BusquedaCodigoView.as_view(), name="buscar_codigo"),
    path("exportar/excel/", ExportarExcelView.as_view(), name="exportar_excel"),
    path("exportar/pdf/", ExportarPdfView.as_view(), name="exportar_pdf"),
]
