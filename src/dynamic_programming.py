"""Programación Dinámica para el problema del cambio de moneda.

Este módulo implementa el enfoque de programación dinámica bottom-up
que encuentra la solución óptima construyendo una tabla de resultados
para todos los subproblemas desde 0 hasta el monto objetivo.

Complexity:
    Time: O(m * n), donde m = amount y n = número de denominaciones.
    Space: O(m), donde m = amount (para el arreglo dp).

Note:
    Siempre encuentra la solución óptima. Es uno de los enfoques
    más equilibrados entre eficiencia y optimalidad para este problema.
"""


class DPResult:
    """Resultado del algoritmo de programación dinámica.

    Attributes:
        coins_used: Lista de monedas que forman la solución óptima.
        count: Cantidad total de monedas usadas.
        optimal: Siemple True (DP siempre encuentra el óptimo).
        dp_table: Tabla de memoización para visualización.
        table_html: Tabla formateada como lista de filas para renderizar.
    """

    def __init__(
        self,
        coins_used: list[int],
        count: int,
        optimal: bool,
        dp_table: list,
        table_rows: list[dict],
    ):
        self.coins_used = coins_used
        self.count = count
        self.optimal = optimal
        self.dp_table = dp_table
        self.table_rows = table_rows


def coin_change_dp(coins: list[int], amount: int) -> DPResult:
    """Resuelve el cambio de moneda usando programación dinámica bottom-up.

    Estrategia:
        Construye una tabla dp donde dp[i] = (mínimo de monedas para monto i).
        Luego reconstruye la solución recorriendo la tabla hacia atrás.

    Args:
        coins: Lista de denominaciones disponibles.
        amount: Cantidad objetivo a formar. Debe ser >= 0.

    Returns:
        DPResult con la solución óptima y la tabla dp para visualización.

    Examples:
        >>> result = coin_change_dp([1, 5, 6], 11)
        >>> result.coins_used
        [5, 6]
        >>> result.count
        2

        >>> result = coin_change_dp([1, 5, 6], 0)
        >>> result.coins_used
        []
        >>> result.count
        0
    """
    if amount == 0:
        return DPResult(
            coins_used=[],
            count=0,
            optimal=True,
            dp_table=[],
            table_rows=[],
        )

    # dp[i] = (mínimo de monedas para monto i, -1 si no es posible)
    INF = float('inf')
    dp = [INF] * (amount + 1)
    dp[0] = 0

    # coin_used[i] = denominación usada para alcanzar monto i (para reconstrucción)
    coin_used = [-1] * (amount + 1)

    # Llenar la tabla dp
    for current_amount in range(1, amount + 1):
        for coin in coins:
            if coin <= current_amount:
                candidate = dp[current_amount - coin] + 1
                if candidate < dp[current_amount]:
                    dp[current_amount] = candidate
                    coin_used[current_amount] = coin

    # Preparar filas de la tabla para visualización en web
    table_rows = []
    for i in range(amount + 1):
        row = {
            'amount': i,
            'min_coins': int(dp[i]) if dp[i] != INF else -1,
            'coin_used': coin_used[i] if coin_used[i] != -1 else '',
        }
        table_rows.append(row)

    # Reconstruir la solución
    coins_used: list[int] = []
    if dp[amount] != INF:
        remaining = amount
        while remaining > 0:
            coin = coin_used[remaining]
            if coin == -1:
                break
            coins_used.append(coin)
            remaining -= coin

    optimal = dp[amount] != INF

    return DPResult(
        coins_used=coins_used,
        count=len(coins_used),
        optimal=optimal,
        dp_table=dp,
        table_rows=table_rows,
    )
