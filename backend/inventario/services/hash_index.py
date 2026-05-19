"""
Índice tipo tabla hash para búsqueda O(1) promedio por ID y por código de barras.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, Optional


def construir_indice_productos(productos: Iterable[Any]) -> Dict[str, Any]:
    """
    Retorna un dict con claves 'id_<int>' y 'bc_<str>' (código de barras normalizado).
    """
    idx: Dict[str, Any] = {}
    for p in productos:
        idx[f"id_{p.id}"] = p
        bc = (getattr(p, "codigo_barras", None) or "").strip()
        if bc:
            idx[f"bc_{bc}"] = p
    return idx


def buscar_por_id(indice: Dict[str, Any], producto_id: int) -> Optional[Any]:
    return indice.get(f"id_{producto_id}")


def buscar_por_codigo_barras(indice: Dict[str, Any], codigo: str) -> Optional[Any]:
    if not codigo:
        return None
    return indice.get(f"bc_{codigo.strip()}")
