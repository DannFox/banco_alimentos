from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Tuple

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import PerfilUsuario, Rol
from inventario.models import Movimiento, Producto, TipoMovimiento


@dataclass(frozen=True)
class MovimientoSpec:
    dias_atras: int
    tipo: str
    cantidad: int
    nota: str


@dataclass(frozen=True)
class ProductoSpec:
    nombre: str
    codigo_barras: str
    dias_para_vencer: int
    movimientos: Tuple[MovimientoSpec, ...]


def _pick_usuario() -> Optional[User]:
    """Elige un usuario razonable para atribuir movimientos."""
    # 1) Admin por perfil
    admin = (
        User.objects.select_related("perfil")
        .filter(perfil__rol=Rol.ADMINISTRADOR)
        .order_by("id")
        .first()
    )
    if admin:
        return admin

    # 2) Superuser
    su = User.objects.filter(is_superuser=True).order_by("id").first()
    if su:
        PerfilUsuario.objects.get_or_create(
            user=su,
            defaults={"nombre_completo": su.get_full_name() or su.username, "rol": Rol.ADMINISTRADOR},
        )
        su.perfil.rol = Rol.ADMINISTRADOR
        su.perfil.save(update_fields=["rol"])
        return su

    # 3) Cualquier usuario existente
    any_user = User.objects.order_by("id").first()
    if any_user:
        PerfilUsuario.objects.get_or_create(
            user=any_user,
            defaults={"nombre_completo": any_user.get_full_name() or any_user.username},
        )
        return any_user

    return None


def _ajustar_stock(producto: Producto, tipo: str, cantidad: int) -> None:
    if tipo == TipoMovimiento.ENTRADA:
        producto.cantidad += cantidad
    else:
        if producto.cantidad < cantidad:
            raise ValueError(
                f"Stock insuficiente para salida. Producto={producto.id} disponible={producto.cantidad} salida={cantidad}"
            )
        producto.cantidad -= cantidad
    producto.save(update_fields=["cantidad", "actualizado_en"])


def _crear_movimiento(
    *,
    producto: Producto,
    usuario: Optional[User],
    tipo: str,
    cantidad: int,
    nota: str,
    registrado_en: Optional[datetime] = None,
) -> Movimiento:
    mov = Movimiento.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        nota=nota,
        usuario=usuario,
    )
    _ajustar_stock(producto, tipo, cantidad)

    if registrado_en is not None:
        Movimiento.objects.filter(pk=mov.pk).update(registrado_en=registrado_en)
        mov.registrado_en = registrado_en
    return mov


def _specs() -> List[ProductoSpec]:
    # Vencimientos distribuidos: vencidos, críticos, urgentes, próximos, normales, y sin stock.
    return [
        ProductoSpec(
            nombre="Arroz blanco 1kg",
            codigo_barras="DEMO-BA-0001",
            dias_para_vencer=60,
            movimientos=(
                MovimientoSpec(12, TipoMovimiento.ENTRADA, 80, "Donación supermercado"),
                MovimientoSpec(5, TipoMovimiento.SALIDA, 10, "Entrega a comedor"),
                MovimientoSpec(1, TipoMovimiento.SALIDA, 6, "Canasta familiar"),
            ),
        ),
        ProductoSpec(
            nombre="Frijoles rojos 1lb",
            codigo_barras="DEMO-BA-0002",
            dias_para_vencer=35,
            movimientos=(
                MovimientoSpec(15, TipoMovimiento.ENTRADA, 50, "Compra mayorista"),
                MovimientoSpec(7, TipoMovimiento.SALIDA, 8, "Entrega a albergue"),
            ),
        ),
        ProductoSpec(
            nombre="Leche UHT 1L",
            codigo_barras="DEMO-BA-0003",
            dias_para_vencer=6,
            movimientos=(
                MovimientoSpec(6, TipoMovimiento.ENTRADA, 30, "Donación"),
                MovimientoSpec(2, TipoMovimiento.SALIDA, 5, "Ración diaria"),
            ),
        ),
        ProductoSpec(
            nombre="Aceite vegetal 900ml",
            codigo_barras="DEMO-BA-0004",
            dias_para_vencer=120,
            movimientos=(
                MovimientoSpec(20, TipoMovimiento.ENTRADA, 25, "Compra"),
                MovimientoSpec(3, TipoMovimiento.SALIDA, 2, "Apoyo cocina"),
            ),
        ),
        ProductoSpec(
            nombre="Pasta espagueti 500g",
            codigo_barras="DEMO-BA-0005",
            dias_para_vencer=14,
            movimientos=(
                MovimientoSpec(9, TipoMovimiento.ENTRADA, 60, "Donación"),
                MovimientoSpec(4, TipoMovimiento.SALIDA, 12, "Canastas"),
            ),
        ),
        ProductoSpec(
            nombre="Atún en lata 140g",
            codigo_barras="DEMO-BA-0006",
            dias_para_vencer=300,
            movimientos=(
                MovimientoSpec(30, TipoMovimiento.ENTRADA, 40, "Donación empresa"),
                MovimientoSpec(10, TipoMovimiento.SALIDA, 4, "Entrega"),
            ),
        ),
        ProductoSpec(
            nombre="Sardinas en lata 155g",
            codigo_barras="DEMO-BA-0007",
            dias_para_vencer=2,
            movimientos=(
                MovimientoSpec(3, TipoMovimiento.ENTRADA, 20, "Donación (próximo a vencer)"),
                MovimientoSpec(1, TipoMovimiento.SALIDA, 6, "Salida urgente"),
            ),
        ),
        ProductoSpec(
            nombre="Harina de maíz 1kg",
            codigo_barras="DEMO-BA-0008",
            dias_para_vencer=8,
            movimientos=(
                MovimientoSpec(8, TipoMovimiento.ENTRADA, 35, "Donación"),
            ),
        ),
        ProductoSpec(
            nombre="Azúcar 1kg",
            codigo_barras="DEMO-BA-0009",
            dias_para_vencer=180,
            movimientos=(
                MovimientoSpec(25, TipoMovimiento.ENTRADA, 20, "Compra"),
                MovimientoSpec(2, TipoMovimiento.SALIDA, 1, "Consumo interno"),
            ),
        ),
        ProductoSpec(
            nombre="Sal yodada 500g",
            codigo_barras="DEMO-BA-0010",
            dias_para_vencer=365,
            movimientos=(
                MovimientoSpec(40, TipoMovimiento.ENTRADA, 15, "Donación"),
            ),
        ),
        ProductoSpec(
            nombre="Galletas integrales",
            codigo_barras="DEMO-BA-0011",
            dias_para_vencer=1,
            movimientos=(
                MovimientoSpec(2, TipoMovimiento.ENTRADA, 18, "Donación (vencimiento cercano)"),
                MovimientoSpec(1, TipoMovimiento.SALIDA, 4, "Salida urgente"),
            ),
        ),
        ProductoSpec(
            nombre="Cereal fortificado",
            codigo_barras="DEMO-BA-0012",
            dias_para_vencer=-2,
            movimientos=(
                MovimientoSpec(12, TipoMovimiento.ENTRADA, 10, "Lote antiguo"),
                MovimientoSpec(11, TipoMovimiento.SALIDA, 10, "Retiro por vencimiento"),
            ),
        ),
        ProductoSpec(
            nombre="Avena 500g",
            codigo_barras="DEMO-BA-0013",
            dias_para_vencer=21,
            movimientos=(
                MovimientoSpec(18, TipoMovimiento.ENTRADA, 22, "Donación"),
                MovimientoSpec(6, TipoMovimiento.SALIDA, 3, "Entrega"),
            ),
        ),
        ProductoSpec(
            nombre="Lentejas 1lb",
            codigo_barras="DEMO-BA-0014",
            dias_para_vencer=45,
            movimientos=(
                MovimientoSpec(22, TipoMovimiento.ENTRADA, 28, "Compra"),
            ),
        ),
        ProductoSpec(
            nombre="Garbanzos 1lb",
            codigo_barras="DEMO-BA-0015",
            dias_para_vencer=10,
            movimientos=(
                MovimientoSpec(10, TipoMovimiento.ENTRADA, 12, "Donación"),
                MovimientoSpec(2, TipoMovimiento.SALIDA, 2, "Entrega"),
            ),
        ),
        ProductoSpec(
            nombre="Puré de tomate 210g",
            codigo_barras="DEMO-BA-0016",
            dias_para_vencer=5,
            movimientos=(
                MovimientoSpec(7, TipoMovimiento.ENTRADA, 16, "Donación"),
                MovimientoSpec(1, TipoMovimiento.SALIDA, 3, "Cocina"),
            ),
        ),
        ProductoSpec(
            nombre="Sopa instantánea",
            codigo_barras="DEMO-BA-0017",
            dias_para_vencer=90,
            movimientos=(
                MovimientoSpec(5, TipoMovimiento.ENTRADA, 0, "Sin stock (demostración)"),
            ),
        ),
        ProductoSpec(
            nombre="Maíz dulce en lata 340g",
            codigo_barras="DEMO-BA-0018",
            dias_para_vencer=200,
            movimientos=(
                MovimientoSpec(16, TipoMovimiento.ENTRADA, 14, "Donación"),
                MovimientoSpec(9, TipoMovimiento.SALIDA, 2, "Entrega"),
            ),
        ),
        ProductoSpec(
            nombre="Café molido 250g",
            codigo_barras="DEMO-BA-0019",
            dias_para_vencer=28,
            movimientos=(
                MovimientoSpec(21, TipoMovimiento.ENTRADA, 8, "Compra"),
                MovimientoSpec(3, TipoMovimiento.SALIDA, 1, "Consumo interno"),
            ),
        ),
    ]


class Command(BaseCommand):
    help = "Carga datos de ejemplo (productos + movimientos) para demostrar el sistema."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reseed",
            action="store_true",
            help="Re-sembra los productos DEMO (borra movimientos de esos productos y recalcula stock).",
        )
        parser.add_argument(
            "--only-if-empty",
            action="store_true",
            help="Solo si no hay productos en la BD (modo seguro).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reseed: bool = bool(options["reseed"])
        only_if_empty: bool = bool(options["only_if_empty"])

        if only_if_empty and Producto.objects.exists():
            self.stdout.write(self.style.WARNING("Ya existen productos; no se sembró nada (usa --reseed si quieres)."))
            return

        usuario = _pick_usuario()
        if usuario is None:
            self.stderr.write(
                self.style.ERROR(
                    "No hay usuarios en la BD. Crea uno (registro o superusuario) y vuelve a ejecutar el seed."
                )
            )
            return

        hoy = timezone.localdate()
        now = timezone.localtime(timezone.now())

        creados = 0
        actualizados = 0
        mov_creados = 0

        for spec in _specs():
            vence = hoy + timedelta(days=spec.dias_para_vencer)

            p = Producto.objects.filter(codigo_barras=spec.codigo_barras).order_by("id").first()
            if p is None:
                p = Producto.objects.create(
                    nombre=spec.nombre,
                    codigo_barras=spec.codigo_barras,
                    cantidad=0,
                    fecha_vencimiento=vence,
                )
                creados += 1
            else:
                p.nombre = spec.nombre
                p.fecha_vencimiento = vence
                if reseed:
                    # Recalcular stock desde cero y reiniciar historial.
                    Movimiento.objects.filter(producto=p).delete()
                    p.cantidad = 0
                p.save(update_fields=["nombre", "fecha_vencimiento", "cantidad", "actualizado_en"])
                actualizados += 1

            # Si es nuevo, tendrá 0 movimientos. Si ya existía, solo sembramos si no tiene historial,
            # salvo que se pida --reseed.
            if reseed or (p.movimientos.count() == 0):
                for ms in spec.movimientos:
                    if ms.cantidad <= 0:
                        continue
                    dt = now - timedelta(days=ms.dias_atras)
                    _crear_movimiento(
                        producto=p,
                        usuario=usuario,
                        tipo=ms.tipo,
                        cantidad=ms.cantidad,
                        nota=ms.nota,
                        registrado_en=dt,
                    )
                    mov_creados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completo. Productos creados: {creados}. Productos actualizados: {actualizados}. Movimientos creados: {mov_creados}."
            )
        )
        self.stdout.write("Ejemplos de códigos para buscar en la UI:")
        for bc in ["DEMO-BA-0003", "DEMO-BA-0007", "DEMO-BA-0011"]:
            self.stdout.write(f"- {bc}")
