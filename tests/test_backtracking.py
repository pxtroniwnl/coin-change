"""Tests unitarios para el algoritmo de backtracking."""

from src.backtracking import coin_change_backtracking


class TestCoinChangeBacktracking:
    """Pruebas para el algoritmo de backtracking."""

    def test_monto_cero(self):
        """Monto 0 debe retornar lista vacía."""
        result = coin_change_backtracking([1, 5, 10], 0)
        assert result.coins_used == []
        assert result.count == 0
        assert result.optimal is True

    def test_sistema_canonico(self):
        """Sistema [1,5,10,25] para monto 30: debe encontrar 25+5."""
        result = coin_change_backtracking([1, 5, 10, 25], 30)
        assert result.count == 2

    def test_sistema_no_canonico(self):
        """Sistema [1,5,6] para monto 11: debe encontrar 6+5 (2 monedas)."""
        result = coin_change_backtracking([1, 5, 6], 11)
        assert result.count == 2

    def test_valor_exacto(self):
        """Monto igual a una denominación debe usar 1 moneda."""
        result = coin_change_backtracking([1, 5, 10, 25], 25)
        assert result.count == 1

    def test_sin_solucion(self):
        """Si no hay moneda de 1, no hay solución."""
        result = coin_change_backtracking([5, 10], 3)
        assert result.count == 0
        assert result.optimal is False

    def test_nodes_explored_tracked(self):
        """Debe rastrear nodos explorados y llamadas recursivas."""
        result = coin_change_backtracking([1, 5], 5)
        assert result.nodes_explored > 0
        assert result.recursive_calls > 0

    def test_optimal_always(self):
        """Backtracking siempre encuentra el óptimo."""
        result = coin_change_backtracking([1, 3, 4], 6)
        assert result.count == 2  # 3 + 3
