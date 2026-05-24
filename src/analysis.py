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
    greedy_gap_graph = _generate_greedy_gap_graph(points, coins)
    summary = _build_summary(points, coins, max_amount)
    complexity_table = _build_complexity_table()
    greedy_gap_summary = _build_greedy_gap_summary(points)

    return {
        'points': points,
        'graph_path': time_graph,
        'coins_used_graph_path': coins_graph,
        'memory_graph_path': memory_graph,
        'greedy_gap_graph_path': greedy_gap_graph,
        'summary': summary,
        'complexity_table': complexity_table,
        'greedy_gap_summary': greedy_gap_summary,
    }


def _build_complexity_table() -> list[dict[str, str]]:
    """Retorna la tabla comparativa teorica de los tres enfoques."""
    return [
        {
            'algorithm': 'Greedy',
            'paradigm': 'Voraz',
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)',
            'guarantees_optimal': 'No',
            'note': 'Muy rapido, pero puede fallar en sistemas no canonicos.',
        },
        {
            'algorithm': 'Programacion Dinamica',
            'paradigm': 'Bottom-up',
            'time_complexity': 'O(m x n)',
            'space_complexity': 'O(m)',
            'guarantees_optimal': 'Si',
            'note': 'Mejor opcion general cuando se necesita optimalidad.',
        },
        {
            'algorithm': 'Backtracking',
            'paradigm': 'Busqueda exhaustiva con poda',
            'time_complexity': 'Exponencial',
            'space_complexity': 'O(profundidad)',
            'guarantees_optimal': 'Si',
            'note': 'Util para explicar el problema; poco adecuado para montos grandes.',
        },
    ]


def _build_summary(
    points: list[dict[str, Any]],
    coins: list[int],
    max_amount: int,
) -> dict[str, Any]:
    """Calcula ganadores practicos de tiempo y memoria en montos comparables."""
    labels = {
        'greedy': 'Greedy',
        'dp': 'Programacion Dinamica',
        'backtracking': 'Backtracking',
    }
    comparable_amounts = sorted(
        set(p['amount'] for p in points if p['algorithm'] == 'greedy')
        & set(p['amount'] for p in points if p['algorithm'] == 'dp')
        & set(p['amount'] for p in points if p['algorithm'] == 'backtracking')
    )
    comparable_points = [
        p for p in points
        if p['amount'] in comparable_amounts and p['coins_used'] >= 0
    ]

    averages: dict[str, dict[str, float]] = {}
    for alg in ['greedy', 'dp', 'backtracking']:
        alg_points = [p for p in comparable_points if p['algorithm'] == alg]
        if not alg_points:
            continue
        averages[alg] = {
            'avg_time_ms': sum(p['time_ms'] for p in alg_points) / len(alg_points),
            'avg_memory_kb': sum(p['memory_kb'] for p in alg_points) / len(alg_points),
        }

    fastest = min(averages, key=lambda alg: averages[alg]['avg_time_ms'])
    lowest_memory = min(averages, key=lambda alg: averages[alg]['avg_memory_kb'])

    return {
        'coins': coins,
        'max_amount': max_amount,
        'comparable_until': comparable_amounts[-1] if comparable_amounts else 0,
        'fastest': labels[fastest],
        'fastest_time_ms': averages[fastest]['avg_time_ms'],
        'lowest_memory': labels[lowest_memory],
        'lowest_memory_kb': averages[lowest_memory]['avg_memory_kb'],
        'recommended': 'Programacion Dinamica',
        'least_suitable_large_amounts': 'Backtracking',
        'averages': [
            {
                'algorithm': labels[alg],
                'avg_time_ms': averages[alg]['avg_time_ms'],
                'avg_memory_kb': averages[alg]['avg_memory_kb'],
            }
            for alg in ['greedy', 'dp', 'backtracking']
            if alg in averages
        ],
    }


def _build_greedy_gap_summary(points: list[dict[str, Any]]) -> dict[str, Any]:
    """Resume cuando Greedy usa mas monedas que Programacion Dinamica."""
    greedy_by_amount = {
        p['amount']: p for p in points
        if p['algorithm'] == 'greedy' and p['coins_used'] >= 0
    }
    dp_by_amount = {
        p['amount']: p for p in points
        if p['algorithm'] == 'dp' and p['coins_used'] >= 0
    }

    gaps = []
    for amount in sorted(set(greedy_by_amount) & set(dp_by_amount)):
        greedy_count = greedy_by_amount[amount]['coins_used']
        dp_count = dp_by_amount[amount]['coins_used']
        gap = greedy_count - dp_count
        if gap > 0:
            gaps.append({
                'amount': amount,
                'greedy_count': greedy_count,
                'dp_count': dp_count,
                'gap': gap,
            })

    return {
        'failures': gaps,
        'failure_count': len(gaps),
        'first_failure': gaps[0] if gaps else None,
        'max_gap': max((gap['gap'] for gap in gaps), default=0),
        'total_extra_coins': sum(gap['gap'] for gap in gaps),
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


def _generate_greedy_gap_graph(
    points: list[dict[str, Any]],
    coins: list[int],
) -> str:
    """Genera grafico de monedas extra usadas por Greedy frente a DP."""
    greedy_by_amount = {
        p['amount']: p for p in points
        if p['algorithm'] == 'greedy' and p['coins_used'] >= 0
    }
    dp_by_amount = {
        p['amount']: p for p in points
        if p['algorithm'] == 'dp' and p['coins_used'] >= 0
    }

    amounts = sorted(set(greedy_by_amount) & set(dp_by_amount))
    gaps = [
        max(0, greedy_by_amount[amount]['coins_used'] - dp_by_amount[amount]['coins_used'])
        for amount in amounts
    ]

    fig, ax = plt.subplots()
    ax.bar(amounts, gaps, color='#ffd700', edgecolor='#664f00', width=3.5)
    ax.set_xlabel('Monto objetivo')
    ax.set_ylabel('Monedas extra de Greedy')
    ax.set_title(f'Brecha Greedy vs DP (monedas: {coins})')
    ax.grid(True, axis='y', alpha=0.3)

    if not any(gaps):
        ax.text(
            0.5,
            0.5,
            'Greedy coincide con DP en los montos evaluados',
            transform=ax.transAxes,
            ha='center',
            va='center',
            fontsize=12,
            color='#333333',
        )

    path = os.path.join(GRAPHS_DIR, 'greedy_gap_analysis.png')
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    return 'static/graphs/greedy_gap_analysis.png'
