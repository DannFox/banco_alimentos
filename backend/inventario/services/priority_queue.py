"""
Cola de prioridad (heap mínimo) por fecha de vencimiento.
Los productos con vencimiento más próximo tienen mayor prioridad de salida (FEFO).
"""
from __future__ import annotations

import heapq
from typing import Iterable, List, Any, Tuple


def construir_cola_prioridad(productos: Iterable[Any]) -> List[Tuple[int, int, Any]]:
    """
    productos: queryset o lista con id, fecha_vencimiento, cantidad.
    Cada elemento del heap: (ordinal_vencimiento, id_producto, objeto_producto).
    """
    heap: list[Tuple[int, int, Any]] = []
    for p in productos:
        if getattr(p, "cantidad", 0) and getattr(p, "fecha_vencimiento", None) is not None:
            ord_fecha = p.fecha_vencimiento.toordinal()
            heapq.heappush(heap, (ord_fecha, p.id, p))
    return heap


def extraer_orden_salida(heap: List[Tuple[int, int, Any]]) -> list:
    """Devuelve productos en orden FEFO (first expire, first out)."""
    h = list(heap)
    heapq.heapify(h)
    orden = []
    while h:
        _, _pid, prod = heapq.heappop(h)
        orden.append(prod)
    return orden
