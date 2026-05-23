"""Aplicación web FastAPI para el problema del cambio de moneda.

Proporciona una interfaz web interactiva para ejecutar los tres
algoritmos de cambio de moneda (voraz, DP, backtracking) y generar
gráficos comparativos de rendimiento.

Endpoints:
    GET  /              : Página principal con formulario.
    POST /solve         : Ejecuta algoritmos seleccionados y muestra resultados.
    GET  /analysis      : Página de análisis comparativo.
    POST /analysis      : Ejecuta benchmarks y genera gráficos.
    GET  /api/solve     : Endpoint REST JSON para resolver.
"""

import time
from pathlib import Path

import jinja2
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.coins import PREDEFINED_COIN_SYSTEMS
from src.greedy import coin_change_greedy
from src.dynamic_programming import coin_change_dp
from src.backtracking import coin_change_backtracking
from src.analysis import run_analysis

# ---------------------------------------------------------------------------
# Inicialización de la aplicación
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title='Coin Change - Cambio de Moneda',
    description='Tres enfoques algorítmicos para el problema del cambio de moneda',
    version='1.0.0',
)

app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(BASE_DIR / 'templates')),
    autoescape=True,
    auto_reload=True,
    cache_size=0,
)
templates = Jinja2Templates(env=jinja_env)


# ---------------------------------------------------------------------------
# Endpoints HTML
# ---------------------------------------------------------------------------


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    """Página principal con formulario para resolver el cambio de moneda."""
    return templates.TemplateResponse(
        request,
        'index.html',
        {
            'coin_systems': PREDEFINED_COIN_SYSTEMS,
        },
    )


@app.post('/solve', response_class=HTMLResponse, include_in_schema=False)
async def solve(
    request: Request,
    coins: str = Form(...),
    amount: int = Form(...),
    algorithms: list[str] = Form(default=[]),
):
    """Ejecuta los algoritmos seleccionados y muestra los resultados.

    Args:
        request: Objeto de petición FastAPI.
        coins: String de denominaciones separadas por coma.
        amount: Monto objetivo a formar.
        algorithms: Lista de algoritmos a ejecutar.

    Returns:
        Página HTML con los resultados de cada algoritmo.
    """
    if not algorithms:
        return templates.TemplateResponse(
            request,
            'result.html',
            {
                'error': 'Debes seleccionar al menos un algoritmo.',
                'amount': amount,
                'request_coins': coins,
                'results': [],
            },
        )

    try:
        coins_list = sorted([int(c.strip()) for c in coins.split(',') if c.strip()])
        if not coins_list:
            raise ValueError('Debe proporcionar al menos una denominación.')
        if min(coins_list) <= 0:
            raise ValueError('Las denominaciones deben ser enteros positivos.')
    except ValueError as e:
        return templates.TemplateResponse(
            request,
            'result.html',
            {
                'error': f'Error en las denominaciones: {e}',
                'amount': amount,
                'request_coins': coins,
                'results': [],
            },
        )

    results = []

    for alg in algorithms:
        start = time.perf_counter()

        try:
            if alg == 'greedy':
                result = coin_change_greedy(coins_list, amount)
                details = {
                    'steps': result.steps,  # ya son dicts, no hay que re-mapear
                }
                
                results.append({
                    'algorithm': 'greedy',
                    'coins_used': result.coins_used,
                    'count': result.count,
                    'optimal': result.optimal,
                    'time_ms': (time.perf_counter() - start) * 1000,
                    'details': details,
                })

            elif alg == 'dp':
                result = coin_change_dp(coins_list, amount)
                details = {
                    'dp_table': result.table_rows,
                }
                results.append({
                    'algorithm': 'dp',
                    'coins_used': result.coins_used,
                    'count': result.count,
                    'optimal': result.optimal,
                    'time_ms': (time.perf_counter() - start) * 1000,
                    'details': details,
                })

            elif alg == 'backtracking':
                BACKTRACKING_LIMIT = 60
                if amount > BACKTRACKING_LIMIT:
                    results.append({
                        'algorithm': 'backtracking',
                        'coins_used': [],
                        'count': 0,
                        'optimal': False,
                        'time_ms': -1,
                        'details': {
                            'error': (
                                f'Monto {amount} supera el límite seguro para Backtracking '
                                f'(máx. {BACKTRACKING_LIMIT}). Su complejidad O(2ⁿ) haría '
                                f'el servidor no responder. Usa Programación Dinámica para montos grandes.'
                            )
                        },
                    })
                else:
                    result = coin_change_backtracking(coins_list, amount)
                    details = {
                        'nodes_explored': result.nodes_explored,
                        'recursive_calls': result.recursive_calls,
                    }
                    results.append({
                        'algorithm': 'backtracking',
                        'coins_used': result.coins_used,
                        'count': result.count,
                        'optimal': result.optimal,
                        'time_ms': (time.perf_counter() - start) * 1000,
                        'details': details,
                    })

        except RecursionError:
            results.append({
                'algorithm': alg,
                'coins_used': [],
                'count': 0,
                'optimal': False,
                'time_ms': -1,
                'details': {
                    'error': 'Límite de recursión excedido. '
                             'Monto muy grande para backtracking.'
                },
            })
        except Exception as e:
            results.append({
                'algorithm': alg,
                'coins_used': [],
                'count': 0,
                'optimal': False,
                'time_ms': -1,
                'details': {'error': str(e)},
            })

    # Verificar optimalidad real del Greedy comparando con DP
    greedy_r = next((r for r in results if r['algorithm'] == 'greedy'), None)
    dp_r = next((r for r in results if r['algorithm'] == 'dp'), None)

    if greedy_r:
        if dp_r:
            # DP ya corrió — comparar directamente
            greedy_r['optimal'] = (
                greedy_r['count'] == dp_r['count'] and greedy_r['count'] > 0
            )
        else:
            # DP no fue seleccionado — correrlo solo para verificar
            dp_check = coin_change_dp(coins_list, amount)
            greedy_r['optimal'] = (
                greedy_r['count'] == dp_check.count and greedy_r['count'] > 0
            )

    # Ordenar resultados: greedy, dp, backtracking
    order = {'greedy': 0, 'dp': 1, 'backtracking': 2}
    results.sort(key=lambda r: order.get(r['algorithm'], 99))

    return templates.TemplateResponse(
        request,
        'result.html',
        {
            'amount': amount,
            'request_coins': coins,
            'results': results,
            'error': None,
        },
    )


@app.get('/analysis', response_class=HTMLResponse, include_in_schema=False)
async def analysis_page(request: Request):
    """Página de análisis comparativo (sin datos iniciales).

    Args:
        request: Objeto de petición FastAPI.

    Returns:
        Página HTML con el formulario de análisis.
    """
    return templates.TemplateResponse(
        request,
        'analysis.html',
        {
            'points': None,
            'graph_path': None,
            'coins_used_graph_path': None,
        },
    )


@app.post('/analysis', response_class=HTMLResponse, include_in_schema=False)
async def run_analysis_page(
    request: Request,
    coins: str = Form(...),
    max_amount: int = Form(200),
):
    """Ejecuta el análisis comparativo y muestra resultados con gráficos.

    Args:
        request: Objeto de petición FastAPI.
        coins: String de denominaciones separadas por coma.
        max_amount: Monto máximo a evaluar.

    Returns:
        Página HTML con gráficos y tabla de datos.
    """
    try:
        coins_list = sorted([int(c.strip()) for c in coins.split(',') if c.strip()])
        if not coins_list:
            raise ValueError('Debe proporcionar al menos una denominación.')
    except ValueError as e:
        return templates.TemplateResponse(
            request,
            'analysis.html',
            {
                'error': str(e),
                'points': None,
                'graph_path': None,
                'coins_used_graph_path': None,
            },
        )

    analysis_result = run_analysis(coins_list, max_amount)

    return templates.TemplateResponse(
        request,
        'analysis.html',
        {
            'points': analysis_result['points'],
            'graph_path': analysis_result['graph_path'],
            'coins_used_graph_path': analysis_result['coins_used_graph_path'],
            'memory_graph_path': analysis_result['memory_graph_path'],
            'error': None,
        },
    )


# ---------------------------------------------------------------------------
# Endpoint REST JSON
# ---------------------------------------------------------------------------


@app.get('/api/solve')
async def api_solve(
    coins: str, amount: int,
    algorithms: str = 'greedy,dp,backtracking',
):
    """Endpoint REST que resuelve el cambio de moneda y retorna JSON.

    Args:
        coins: Denominaciones separadas por coma (ej: '1,5,6').
        amount: Monto objetivo.
        algorithms: Algoritmos separados por coma (ej: 'greedy,dp').

    Returns:
        JSON con los resultados de cada algoritmo.
    """
    try:
        coins_list = sorted([int(c.strip()) for c in coins.split(',') if c.strip()])
        alg_list = [a.strip() for a in algorithms.split(',') if a.strip()]

        if not coins_list:
            return JSONResponse(
                status_code=400,
                content={'error': 'Debe proporcionar al menos una denominación.'},
            )
        if amount < 0:
            return JSONResponse(
                status_code=400,
                content={'error': 'El monto debe ser un entero no negativo.'},
            )

        results = []

        for alg in alg_list:
            if alg not in ('greedy', 'dp', 'backtracking'):
                continue

            start = time.perf_counter()

            if alg == 'greedy':
                result = coin_change_greedy(coins_list, amount)
                results.append({
                    'algorithm': 'greedy',
                    'coins_used': result.coins_used,
                    'count': result.count,
                    'optimal': result.optimal,
                    'time_ms': round((time.perf_counter() - start) * 1000, 4),
                })
            elif alg == 'dp':
                result = coin_change_dp(coins_list, amount)
                results.append({
                    'algorithm': 'dp',
                    'coins_used': result.coins_used,
                    'count': result.count,
                    'optimal': result.optimal,
                    'time_ms': round((time.perf_counter() - start) * 1000, 4),
                })
            elif alg == 'backtracking':
                result = coin_change_backtracking(coins_list, amount)
                results.append({
                    'algorithm': 'backtracking',
                    'coins_used': result.coins_used,
                    'count': result.count,
                    'optimal': result.optimal,
                    'time_ms': round((time.perf_counter() - start) * 1000, 4),
                })

        order = {'greedy': 0, 'dp': 1, 'backtracking': 2}
        results.sort(key=lambda r: order.get(r['algorithm'], 99))

        return {
            'amount': amount,
            'coins': coins_list,
            'results': results,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'error': str(e)},
        )


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)