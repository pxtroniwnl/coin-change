"""Modelos Pydantic para las peticiones y respuestas de la API.

Define los esquemas de datos utilizados para la comunicación
entre el frontend y los endpoints de FastAPI.
"""

from typing import Literal

from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    """Modelo de petición para resolver el cambio de moneda.

    Attributes:
        coins: Lista de denominaciones disponibles.
        amount: Cantidad objetivo a formar.
        algorithms: Lista de algoritmos a ejecutar.
    """

    coins: list[int] = Field(
        ..., min_length=1, description='Denominaciones disponibles'
    )
    amount: int = Field(..., ge=0, description='Cantidad objetivo a formar')
    algorithms: list[Literal['greedy', 'dp', 'backtracking']] = Field(
        ..., min_length=1, description='Algoritmos a ejecutar'
    )


class AlgorithmResult(BaseModel):
    """Resultado de un algoritmo individual.

    Attributes:
        algorithm: Nombre del algoritmo ejecutado.
        coins_used: Lista de monedas utilizadas en la solución.
        count: Cantidad total de monedas usadas.
        optimal: Indica si la solución es óptima.
        time_ms: Tiempo de ejecución en milisegundos.
        details: Datos adicionales para visualización.
    """

    algorithm: str
    coins_used: list[int]
    count: int
    optimal: bool
    time_ms: float
    details: dict | None = None


class SolveResponse(BaseModel):
    """Modelo de respuesta para una solicitud de solución.

    Attributes:
        amount: Cantidad objetivo procesada.
        results: Lista de resultados por algoritmo.
        error: Mensaje de error si ocurrió alguno.
    """

    amount: int
    results: list[AlgorithmResult]
    error: str | None = None


class AnalysisRequest(BaseModel):
    """Modelo de petición para ejecutar el análisis comparativo.

    Attributes:
        coins: Lista de denominaciones a usar en el análisis.
        max_amount: Monto máximo a probar.
    """

    coins: list[int] = Field(
        ..., min_length=1, description='Denominaciones para el análisis'
    )
    max_amount: int = Field(
        200, ge=10, le=1000, description='Monto máximo a evaluar'
    )


class AnalysisPoint(BaseModel):
    """Punto individual del análisis para un algoritmo y monto.

    Attributes:
        amount: Monto evaluado.
        algorithm: Nombre del algoritmo.
        time_ms: Tiempo de ejecución en milisegundos.
        coins_used: Cantidad de monedas usadas.
    """

    amount: int
    algorithm: str
    time_ms: float
    coins_used: int


class AnalysisResponse(BaseModel):
    """Modelo de respuesta del análisis comparativo.

    Attributes:
        points: Lista de puntos del análisis.
        graph_path: Ruta al gráfico generado.
        coins_used_graph_path: Ruta al gráfico de monedas usadas.
        error: Mensaje de error si ocurrió alguno.
    """

    points: list[AnalysisPoint]
    graph_path: str | None = None
    coins_used_graph_path: str | None = None
    error: str | None = None
