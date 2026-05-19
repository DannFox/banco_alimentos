"""
Estadísticas de una tabla hash simulada (cubetas + encadenamiento) a partir del catálogo real.
Usa función tipo Horner para cadenas y mezcla multiplicativa para IDs, determinista.
"""
from __future__ import annotations

from typing import Any, List, Tuple


def horner_hash_string(s: str) -> int:
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0x7FFFFFFF
    return h


def _idx_id(pid: int, m: int) -> int:
    return ((pid * 2654435761) & 0xFFFFFFFF) % m


def _idx_bc(bc_hash: int, m: int) -> int:
    return bc_hash % m


def computar_estadisticas_hash(productos: List[Any]) -> dict:
    """
    Cada producto aporta una clave `id_<id>`; si tiene código de barras, otra clave `bc_<hash>`.
    Reparte en m cubetas; cuenta colisiones en inserción y cadena máxima.
    """
    claves: List[Tuple[str, int]] = []
    for p in productos:
        claves.append(("id", p.id))
        bc = (getattr(p, "codigo_barras", None) or "").strip()
        if bc:
            claves.append(("bc", horner_hash_string(bc)))

    n = len(claves)
    if n == 0:
        return {
            "total_elementos": 0,
            "productos_catalogo": len(productos),
            "claves_codigo_barras": 0,
            "claves_id": 0,
            "capacidad_cubetas": 64,
            "factor_carga_pct": 0.0,
            "inserciones_con_colision": 0,
            "cubetas_ocupadas": 0,
            "max_cadena": 0,
        }

    m = 64
    while n / m > 0.75:
        m *= 2

    buckets: List[List[str]] = [[] for _ in range(m)]
    colisiones = 0
    for tipo, val in claves:
        idx = _idx_bc(val, m) if tipo == "bc" else _idx_id(val, m)
        if buckets[idx]:
            colisiones += 1
        buckets[idx].append(f"{tipo}:{val}")

    ocupadas = sum(1 for b in buckets if b)
    max_cadena = max((len(b) for b in buckets), default=0)

    return {
        "total_elementos": n,
        "productos_catalogo": len(productos),
        "claves_codigo_barras": sum(1 for t, _ in claves if t == "bc"),
        "claves_id": sum(1 for t, _ in claves if t == "id"),
        "capacidad_cubetas": m,
        "factor_carga_pct": round(100 * n / m, 1),
        "inserciones_con_colision": colisiones,
        "cubetas_ocupadas": ocupadas,
        "max_cadena": max_cadena,
    }
