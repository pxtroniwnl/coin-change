"""Tests unitarios para el algoritmo de programación dinámica."""

from src.dynamic_programming import coin_change_dp


class TestCoinChangeDP:
    """Pruebas para el algoritmo de programación dinámica."""

    def test_monto_cero(self):
        """Monto 0 debe retornar lista vacía."""
        result = coin_change_dp([1, 5, 10], 0)
        assert result.coins_used == []
        assert result.count == 0
        assert result.optimal is True

    def test_sistema_canonico(self):
        """Sistema USD para monto 30: debe ser óptimo (25+5)."""
        result = coin_change_dp([1, 5, 10, 25], 30)
        assert result.count == 2

    def test_sistema_no_canonico(self):
        """Sistema [1,5,6] para monto 11: DP debe encontrar 6+5 (2 monedas)."""
        result = coin_change_dp([1, 5, 6], 11)
        assert result.count == 2

    def test_valor_exacto(self):
        """Monto igual a una denominación debe usar 1 moneda."""
        result = coin_change_dp([1, 5, 10, 25], 25)
        assert result.count == 1
        assert result.coins_used == [25]

    def test_sin_solucion(self):
        """Si no hay moneda de 1, puede no tener solución."""
        result = coin_change_dp([5, 10], 3)
        assert result.count == 0
        assert result.optimal is False

    def test_dp_table_size(self):
        """La tabla dp debe tener amount+1 filas."""
        result = coin_change_dp([1, 5, 10], 10)
        assert len(result.table_rows) == 11

    def test_moneda_unica(self):
        """Una sola denominación."""
        result = coin_change_dp([3], 9)
        assert result.count == 3

    def test_optimal_always(self):
        """DP siempre marca optimal=True cuando encuentra solución."""
        result = coin_change_dp([1, 2, 5], 7)
        assert result.optimal is True
        assert result.count == 2  # 5 + 2
