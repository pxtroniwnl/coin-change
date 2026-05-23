"""Análisis comparativo de los algoritmos de cambio de moneda.

Este módulo ejecuta benchmarks de los tres algoritmos (voraz, DP, backtracking)
con montos crecientes y genera gráficos comparativos de rendimiento.

Dependencies:
    matplotlib: Para la generación de gráficos.
    time: Para medición precisa de tiempos de ejecución.
    tracemalloc: Para medición de uso de memoria.
"""

import os
import time
import tracemalloc
from typing import Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

from src.greedy import coin_change_greedy  # noqa: E402
from src.dynamic_programming import coin_change_dp  # noqa: E402
from src.backtracking import coin_change_backtracking  # noqa: E402

# Configuración global de matplotlib
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

GRAPHS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'static',
    'graphs',
)


def _measure_time(
    algorithm: str,
    coins: list[int],
    amount: int,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Mide el tiempo de ejecución y el uso de memoria pico de un algoritmo.

    Args:
        algorithm: Nombre del algoritmo ('greedy', 'dp', 'backtracking').
        coins: Denominaciones a utilizar.
        amount: Monto objetivo.
        timeout: Tiempo máximo de ejecución en segundos.

    Returns:
        Diccionario con resultado, tiempo, cantidad de monedas y memoria pico en KB.
    """
    tracemalloc.start()
    start = time.perf_counter()

    if algorithm == 'greedy':
        result = coin_change_greedy(coins, amount)
        coins_used = result.count
    elif algorithm == 'dp':
        result = coin_change_dp(coins, amount)
        coins_used = result.count
    elif algorithm == 'backtracking':
        result = coin_change_backtracking(coins, amount)
        coins_used = result.count
    else:
        raise ValueError(f'Algoritmo desconocido: {algorithm}')

    elapsed = (time.perf_counter() - start) * 1000  # ms
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_kb = peak_bytes / 1024  # convertir a KB

    if elapsed > timeout * 1000:
        return {'coins_used': -1, 'time_ms': elapsed, 'memory_kb': peak_kb, 'timed_out': True}

    return {'coins_used': coins_used, 'time_ms': elapsed, 'memory_kb': peak_kb, 'timed_out': False}


def run_analysis(
    coins: list[int],
    max_amount: int = 200,
) -> dict[str, Any]:
    """Ejecuta el análisis comparativo de los tres algoritmos.

    Args:
        coins: Denominaciones a utilizar en el análisis.
        max_amount: Monto máximo a evaluar.

    Returns:
        Diccionario con los puntos de datos y las rutas de los gráficos.

    Note:
        Backtracking se prueba con montos más pequeños debido a su
        alta complejidad computacional.
    """
    os.makedirs(GRAPHS_DIR, exist_ok=True)

    points: list[dict[str, Any]] = []

    amounts_full = list(range(0, max_amount + 1, 5))
    if amounts_full[-1] != max_amount:
        amounts_full.append(max_amount)

    bt_limit = min(60, max_amount)
    amounts_bt = list(range(0, bt_limit + 1, 5))
    if amounts_bt[-1] != bt_limit:
        amounts_bt.append(bt_limit)

    # Recolectar datos para Greedy y DP
    for amount in amounts_full:
        for alg in ['greedy', 'dp']:
            data = _measure_time(alg, coins, amount)
            points.append({
                'amount': amount,
                'algorithm': alg,
                'time_ms': data['time_ms'],
                'coins_used': data['coins_used'],
                'memory_kb': data['memory_kb'],
            })

    # Recolectar datos para Backtracking
    for amount in amounts_bt:
        data = _measure_time('backtracking', coins, amount)
        points.append({
            'amount': amount,
            'algorithm': 'backtracking',
            'time_ms': data['time_ms'],
            'coins_used': data['coins_used'],
            'memory_kb': data['memory_kb'],
        })

    # Generar gráficos
    time_graph = _generate_time_graph(points, coins)
    coins_graph = _generate_coins_graph(points, coins)
    memory_graph = _generate_memory_graph(points, coins)

    return {
        'points': points,
        'graph_path': time_graph,
        'coins_used_graph_path': coins_graph,
        'memory_graph_path': memory_graph,
    }


def _generate_time_graph(
    points: list[dict[str, Any]],
    coins: list[int],
) -> str:
    """Genera gráfico de tiempo de ejecución vs monto."""
    fig, ax = plt.subplots()

    colors = {'greedy': '#2ecc71', 'dp': '#3498db', 'backtracking': '#e74c3c'}
    markers = {'greedy': 'o', 'dp': 's', 'backtracking': '^'}
    labels = {
        'greedy': 'Voraz (Greedy)',
        'dp': 'Programación Dinámica',
        'backtracking': 'Backtracking',
    }

    for alg in ['greedy', 'dp', 'backtracking']:
        alg_points = [p for p in points if p['algorithm'] == alg and not p.get('timed_out')]
        if not alg_points:
            continue
        ax.plot(
            [p['amount'] for p in alg_points],
            [p['time_ms'] for p in alg_points],
            color=colors[alg], marker=markers[alg], label=labels[alg],
            linewidth=2, markersize=4,
        )

    ax.set_xlabel('Monto objetivo')
    ax.set_ylabel('Tiempo de ejecución (ms)')
    ax.set_title(f'Tiempo de ejecución vs Monto objetivo (monedas: {coins})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    path = os.path.join(GRAPHS_DIR, 'time_analysis.png')
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return 'static/graphs/time_analysis.png'


def _generate_coins_graph(
    points: list[dict[str, Any]],
    coins: list[int],
) -> str:
    """Genera gráfico de cantidad de monedas usadas vs monto."""
    fig, ax = plt.subplots()

    colors = {'greedy': '#2ecc71', 'dp': '#3498db', 'backtracking': '#e74c3c'}
    markers = {'greedy': 'o', 'dp': 's', 'backtracking': '^'}
    labels = {
        'greedy': 'Voraz (Greedy)',
        'dp': 'Programación Dinámica',
        'backtracking': 'Backtracking',
    }

    for alg in ['greedy', 'dp', 'backtracking']:
        alg_points = [p for p in points if p['algorithm'] == alg and p['coins_used'] >= 0]
        if not alg_points:
            continue
        ax.plot(
            [p['amount'] for p in alg_points],
            [p['coins_used'] for p in alg_points],
            color=colors[alg], marker=markers[alg], label=labels[alg],
            linewidth=2, markersize=4,
        )

    ax.set_xlabel('Monto objetivo')
    ax.set_ylabel('Cantidad de monedas usadas')
    ax.set_title(f'Cantidad de monedas vs Monto objetivo (monedas: {coins})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    path = os.path.join(GRAPHS_DIR, 'coins_analysis.png')
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return 'static/graphs/coins_analysis.png'


def _generate_memory_graph(
    points: list[dict[str, Any]],
    coins: list[int],
) -> str:
    """Genera gráfico de uso de memoria pico vs monto.

    Muestra la diferencia entre:
        - Greedy:       O(1) — variables simples, casi sin memoria extra.
        - DP:           O(m) — arreglo dp[] de tamaño (monto + 1).
        - Backtracking: O(profundidad) — pila de recursión.

    Args:
        points: Datos del análisis, cada punto incluye 'memory_kb'.
        coins: Denominaciones usadas (para el título).

    Returns:
        Ruta relativa al archivo de imagen generado.
    """
    fig, ax = plt.subplots()

    colors = {'greedy': '#2ecc71', 'dp': '#3498db', 'backtracking': '#e74c3c'}
    markers = {'greedy': 'o', 'dp': 's', 'backtracking': '^'}
    labels = {
        'greedy': 'Voraz — O(1) variables simples',
        'dp': 'Prog. Dinámica — O(m) arreglo dp[]',
        'backtracking': 'Backtracking — O(prof.) pila recursión',
    }

    for alg in ['greedy', 'dp', 'backtracking']:
        alg_points = [p for p in points if p['algorithm'] == alg and not p.get('timed_out')]
        if not alg_points:
            continue
        ax.plot(
            [p['amount'] for p in alg_points],
            [p['memory_kb'] for p in alg_points],
            color=colors[alg], marker=markers[alg], label=labels[alg],
            linewidth=2, markersize=4,
        )

    ax.set_xlabel('Monto objetivo')
    ax.set_ylabel('Memoria pico (KB)')
    ax.set_title(f'Uso de memoria pico vs Monto objetivo (monedas: {coins})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Anotación explicativa dentro del gráfico
    ax.annotate(
        'DP crece linealmente con el monto\n'
        'Backtracking crece con la profundidad de recursión\n'
        'Greedy permanece casi constante',
        xy=(0.02, 0.97),
        xycoords='axes fraction',
        fontsize=9,
        verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f8f8', alpha=0.7),
    )

    path = os.path.join(GRAPHS_DIR, 'memory_analysis.png')
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return 'static/graphs/memory_analysis.png'