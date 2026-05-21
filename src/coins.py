"""Sistemas monetarios predefinidos para el problema del cambio de moneda.

Este módulo contiene denominaciones de diferentes sistemas monetarios
que pueden ser utilizados para probar los algoritmos de cambio de moneda.
"""

from typing import NamedTuple


class CoinSystem(NamedTuple):
    """Representa un sistema monetario con nombre y denominaciones.

    Attributes:
        name: Nombre descriptivo del sistema monetario.
        denominations: Lista de denominaciones disponibles.
        canonical: Indica si el sistema es canónico (greedy da óptimo).
    """

    name: str
    denominations: list[int]
    canonical: bool


# Sistemas monetarios canónicos (greedy siempre encuentra el óptimo)
USD = CoinSystem(
    name='Dólar estadounidense (USD)',
    denominations=[1, 5, 10, 25, 50],
    canonical=True,
)

EUR = CoinSystem(
    name='Euro (EUR)',
    denominations=[1, 2, 5, 10, 20, 50, 100, 200],
    canonical=True,
)

COP = CoinSystem(
    name='Peso colombiano (COP)',
    denominations=[50, 100, 200, 500, 1000],
    canonical=True,
)

# Sistemas no canónicos (greedy puede NO encontrar el óptimo)
NON_CANONICAL_1 = CoinSystem(
    name='Sistema no canónico #1',
    denominations=[1, 5, 6],
    canonical=False,
)

NON_CANONICAL_2 = CoinSystem(
    name='Sistema no canónico #2',
    denominations=[1, 3, 4],
    canonical=False,
)

NON_CANONICAL_3 = CoinSystem(
    name='Sistema no canónico #3',
    denominations=[1, 12, 20, 25],
    canonical=False,
)

# Lista completa de sistemas predefinidos
PREDEFINED_COIN_SYSTEMS: list[CoinSystem] = [
    USD,
    EUR,
    COP,
    NON_CANONICAL_1,
    NON_CANONICAL_2,
    NON_CANONICAL_3,
]


def get_system_by_name(name: str) -> CoinSystem | None:
    """Busca un sistema monetario por su nombre.

    Args:
        name: Nombre del sistema a buscar (case-insensitive).

    Returns:
        CoinSystem si se encuentra, None en caso contrario.
    """
    for system in PREDEFINED_COIN_SYSTEMS:
        if system.name.lower() == name.lower():
            return system
    return None
