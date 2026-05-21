"""Backtracking para el problema del cambio de moneda.

Este módulo implementa un enfoque de backtracking con poda que
explora recursivamente todas las combinaciones posibles de monedas
para encontrar la solución óptima.

Complexity:
    Time: O(2^n) en el peor caso, donde n depende del monto.
    Space: O(amount) en el peor caso por la profundidad de la recursión.

Note:
    Aunque encuentra la solución óptima, su costo computacional
    crece exponencialmente, lo que lo hace impracticable para
    montos grandes. Se incluye con fines comparativos.
"""

import sys


class BacktrackingResult:
    """Resultado del algoritmo de backtracking.

    Attributes:
        coins_used: Lista de monedas que forman la solución óptima.
        count: Cantidad total de monedas usadas.
        optimal: True si encontró solución óptima.
        nodes_explored: Número de nodos (estados) explorados.
        recursive_calls: Número de llamadas recursivas realizadas.
    """

    def __init__(
        self,
        coins_used: list[int],
        count: int,
        optimal: bool,
        nodes_explored: int,
        recursive_calls: int,
    ):
        self.coins_used = coins_used
        self.count = count
        self.optimal = optimal
        self.nodes_explored = nodes_explored
        self.recursive_calls = recursive_calls


def _backtrack(
    coins: list[int],
    remaining: int,
    current_combo: list[int],
    best_combo: list[int],
    best_count: list[int],
    nodes_explored: list[int],
    recursive_calls: list[int],
    start_index: int,
) -> None:
    """Función recursiva interna que explora combinaciones de monedas.

    Args:
        coins: Denominaciones disponibles (ordenadas descendente).
        remaining: Monto restante por formar.
        current_combo: Combinación actual en exploración.
        best_combo: Mejor combinación encontrada hasta ahora.
        best_count: Lista de un elemento con el mejor conteo.
        nodes_explored: Contador de nodos explorados.
        recursive_calls: Contador de llamadas recursivas.
        start_index: Índice desde el cual probar monedas (para poda).
    """
    recursive_calls[0] += 1

    # Poda: si ya superamos la mejor solución, no seguir
    if len(current_combo) >= best_count[0]:
        return

    # Caso base: encontramos una solución
    if remaining == 0:
        if len(current_combo) < best_count[0]:
            best_count[0] = len(current_combo)
            best_combo.clear()
            best_combo.extend(current_combo)
        return

    # Explorar monedas desde start_index (evita permutaciones redundantes)
    for i in range(start_index, len(coins)):
        coin = coins[i]
        if coin > remaining:
            continue

        nodes_explored[0] += 1
        current_combo.append(coin)
        _backtrack(
            coins,
            remaining - coin,
            current_combo,
            best_combo,
            best_count,
            nodes_explored,
            recursive_calls,
            i,  # permite reusar la misma moneda
        )
        current_combo.pop()


def coin_change_backtracking(coins: list[int], amount: int) -> BacktrackingResult:
    """Resuelve el cambio de moneda usando backtracking con poda.

    Estrategia:
        Explora combinaciones recursivamente, podando ramas cuya
        longitud ya iguala o supera la mejor solución encontrada.
        Usa un índice para evitar permutaciones redundantes.

    Args:
        coins: Lista de denominaciones disponibles.
        amount: Cantidad objetivo a formar. Debe ser >= 0.

    Returns:
        BacktrackingResult con la solución óptima y estadísticas
        de exploración.

    Examples:
        >>> result = coin_change_backtracking([5, 6, 1], 11)
        >>> result.coins_used  # Puede ser [5, 6] o [6, 5]
        [5, 6]
        >>> result.count
        2

        >>> result = coin_change_backtracking([1, 5, 6], 0)
        >>> result.coins_used
        []
        >>> result.count
        0
    """
    if amount == 0:
        return BacktrackingResult(
            coins_used=[],
            count=0,
            optimal=True,
            nodes_explored=0,
            recursive_calls=0,
        )

    sys.setrecursionlimit(10000)

    # Ordenar descendente para probar monedas grandes primero
    sorted_coins = sorted(coins, reverse=True)

    current_combo: list[int] = []
    best_combo: list[int] = []
    best_count: list[int] = [float('inf')]  # type: ignore[assignment]
    nodes_explored: list[int] = [0]
    recursive_calls: list[int] = [0]

    _backtrack(
        sorted_coins,
        amount,
        current_combo,
        best_combo,
        best_count,
        nodes_explored,
        recursive_calls,
        0,
    )

    found = best_count[0] != float('inf')

    return BacktrackingResult(
        coins_used=best_combo,
        count=len(best_combo) if found else 0,
        optimal=found,
        nodes_explored=nodes_explored[0],
        recursive_calls=recursive_calls[0],
    )
