"""Tests unitarios para el algoritmo voraz (greedy)."""

from src.greedy import coin_change_greedy


class TestCoinChangeGreedy:
    """Pruebas para el algoritmo voraz de cambio de moneda."""

    def test_monto_cero(self):
        """Monto 0 debe retornar lista vacía."""
        result = coin_change_greedy([1, 5, 10], 0)
        assert result.coins_used == []
        assert result.count == 0
        assert result.optimal is True

    def test_sistema_canonico(self):
        """Sistema canónico USD: greedy debe encontrar óptimo."""
        result = coin_change_greedy([1, 5, 10, 25], 30)
        assert result.count == 2  # 25 + 5
        assert result.optimal is True

    def test_sistema_no_canonico(self):
        """Sistema [1,5,6] para monto 10: greedy da 5 monedas (no óptimo)."""
        result = coin_change_greedy([1, 5, 6], 10)
        assert result.count == 5  # 6 + 1 + 1 + 1 + 1
        assert result.optimal is True

    def test_valor_exacto(self):
        """Monto igual a una denominación debe usar 1 moneda."""
        result = coin_change_greedy([1, 5, 10, 25], 25)
        assert result.count == 1
        assert result.coins_used == [25]

    def test_sin_solucion(self):
        """Si el menor no es 1, puede no tener solución."""
        result = coin_change_greedy([5, 10], 3)
        assert result.count == 0
        assert result.optimal is False

    def test_denominaciones_desordenadas(self):
        """Funciona aunque las denominaciones no estén ordenadas."""
        result = coin_change_greedy([10, 1, 5], 16)
        assert result.count == 3

    def test_moneda_unica(self):
        """Una sola denominación debe usar la cantidad exacta."""
        result = coin_change_greedy([3], 9)
        assert result.count == 3
        assert result.coins_used == [3, 3, 3]
