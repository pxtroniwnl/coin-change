"""Algoritmo Voraz (Greedy) para el problema del cambio de moneda.

Este módulo implementa el enfoque voraz que selecciona siempre
la moneda de mayor denominación que no supere el monto restante.

Complexity:
    Time: O(n), donde n es el número de denominaciones.
    Space: O(1) adicional.

Note:
    No garantiza la solución óptima para sistemas de monedas
    no canónicos. Por ejemplo, con monedas [1, 5, 6] y monto 10,
    el voraz da 6+1+1+1+1 (5 monedas), pero la óptima es 5+5 (2 monedas).
"""

from typing import NamedTuple


class StepInfo(NamedTuple):
    """Información de un paso del algoritmo voraz.

    Attributes:
        coin: Denominación seleccionada en este paso.
        remaining_before: Monto restante antes de tomar la moneda.
        count_at_step: Cantidad de monedas llevadas hasta este paso.
    """

    coin: int
    remaining_before: int
    count_at_step: int


class GreedyResult(NamedTuple):
    """Resultado completo del algoritmo voraz.

    Attributes:
        coins_used: Lista de monedas seleccionadas.
        count: Cantidad total de monedas usadas.
        optimal: True si el algoritmo logro formar el monto exacto.
            La aplicacion verifica la optimalidad real comparando contra DP.
        steps: Lista de pasos para visualización.
    """

    coins_used: list[int]
    count: int
    optimal: bool
    steps: list[dict]


def coin_change_greedy(coins: list[int], amount: int) -> GreedyResult:
    """Resuelve el cambio de moneda usando el algoritmo voraz.

    Estrategia:
        Ordena las denominaciones de mayor a menor e itera
        seleccionando la moneda más grande posible en cada paso.

    Args:
        coins: Lista de denominaciones disponibles (no necesariamente ordenada).
        amount: Cantidad objetivo a formar. Debe ser >= 0.

    Returns:
        GreedyResult con las monedas usadas, cantidad, optimalidad y pasos.

    Examples:
        >>> result = coin_change_greedy([1, 5, 6], 10)
        >>> result.coins_used
        [6, 1, 1, 1, 1]
        >>> result.count
        5

        >>> result = coin_change_greedy([1, 5, 6], 0)
        >>> result.coins_used
        []
        >>> result.count
        0
    """
    if amount == 0:
        return GreedyResult(coins_used=[], count=0, optimal=True, steps=[])

    sorted_coins = sorted(coins, reverse=True)
    remaining = amount
    coins_used: list[int] = []
    steps: list[dict] = []

    for coin in sorted_coins:
        if remaining == 0:
            break
        if coin <= remaining:
            num_coins = remaining // coin
            coins_used.extend([coin] * num_coins)
            remaining -= coin * num_coins
            steps.append({
                'coin': coin,
                'times_used': num_coins,
                'remaining_before': remaining + coin * num_coins,
                'remaining_after': remaining,
                'total_coins_so_far': len(coins_used),
            })

    optimal = remaining == 0

    return GreedyResult(
        coins_used=coins_used,
        count=len(coins_used),
        optimal=optimal,
        steps=steps,
    )
