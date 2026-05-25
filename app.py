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
from urllib.parse import urlencode
import io
import csv

import jinja2
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
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


def parse_coins(coins: str) -> list[int]:
    """Convierte y valida denominaciones separadas por coma."""
    coins_list = sorted([int(c.strip()) for c in coins.split(',') if c.strip()])
    if not coins_list:
        raise ValueError('Debe proporcionar al menos una denominación.')
    if min(coins_list) <= 0:
        raise ValueError('Las denominaciones deben ser enteros positivos.')
    return coins_list


def is_greedy_optimal(
    greedy_count: int,
    greedy_coins: list[int],
    dp_count: int,
    dp_coins: list[int],
    amount: int,
) -> bool:
    """Determina si Greedy igualo la solucion optima de DP."""
    if amount == 0:
        return True
    return bool(greedy_coins) and bool(dp_coins) and greedy_count == dp_count


def build_analysis_context(
    request: Request,
    coins: str | None = None,
    max_amount: int | None = None,
    error: str | None = None,
) -> dict:
    """Crea el contexto de la pagina de analisis, con datos si hay configuracion."""
    context = {
        'request': request,
        'points': None,
        'graph_path': None,
        'coins_used_graph_path': None,
        'memory_graph_path': None,
        'greedy_gap_graph_path': None,
        'summary': None,
        'complexity_table': None,
        'greedy_gap_summary': None,
        'request_coins': coins,
        'max_amount': max_amount,
        'error': error,
    }

    if not coins or error:
        return context

    try:
        coins_list = parse_coins(coins)
        analysis_max_amount = max_amount if max_amount is not None else 200
        if analysis_max_amount < 0:
            raise ValueError('El monto máximo debe ser un entero no negativo.')
    except ValueError as exc:
        context['error'] = str(exc)
        return context

    analysis_result = run_analysis(coins_list, analysis_max_amount)
    context.update({
        'points': analysis_result['points'],
        'graph_path': analysis_result['graph_path'],
        'coins_used_graph_path': analysis_result['coins_used_graph_path'],
        'memory_graph_path': analysis_result['memory_graph_path'],
        'greedy_gap_graph_path': analysis_result['greedy_gap_graph_path'],
        'summary': analysis_result['summary'],
        'complexity_table': analysis_result['complexity_table'],
        'greedy_gap_summary': analysis_result['greedy_gap_summary'],
        'request_coins': ','.join(str(c) for c in coins_list),
        'max_amount': analysis_max_amount,
    })
    return context


def generar_conclusion(results, amount):
    """Genera la conclusión automática comparando el Algoritmo Voraz y DP."""
    greedy_r = next((r for r in results if r['algorithm'] == 'greedy'), None)
    dp_r = next((r for r in results if r['algorithm'] == 'dp'), None)

    if greedy_r and dp_r:
        g_count = greedy_r['count']
        d_count = dp_r['count']
        if g_count == 0 or d_count == 0:
            return "Uno de los algoritmos no encontró solución."
        elif g_count == d_count:
            opt = 'óptimo' if greedy_r['optimal'] and dp_r['optimal'] else 'subóptimo'
            return f"Ambos algoritmos usaron {g_count} monedas. Resultado {opt}. No hay ventaja entre ellos."
        else:
            if greedy_r['optimal'] and not dp_r['optimal']:
                return f"El Algoritmo Voraz obtuvo la solución óptima ({g_count} monedas), mientras que la Programación Dinámica no logró el óptimo ({d_count} monedas). El Algoritmo Voraz es más eficiente en este caso."
            elif not greedy_r['optimal'] and dp_r['optimal']:
                return f"La Programación Dinámica obtuvo la solución óptima ({d_count} monedas), mientras que el Algoritmo Voraz no fue óptimo ({g_count} monedas). La Programación Dinámica es más eficiente en este caso."
            else:
                mejor_alg = 'el Algoritmo Voraz' if g_count < d_count else 'la Programación Dinámica'
                peor_alg = 'la Programación Dinámica' if g_count < d_count else 'el Algoritmo Voraz'
                mejor_count = min(g_count, d_count)
                peor_count = max(g_count, d_count)
                perc = ((peor_count - mejor_count) / peor_count) * 100
                return f"En comparación, {mejor_alg} usó {mejor_count} monedas, mientras que {peor_alg} usó {peor_count}. {mejor_alg} fue más eficiente que {peor_alg} por un {perc:.1f}% en cantidad de monedas."
    return None


def obtener_resultados_para_exportar(coins_list, amount, alg_list):
    """Ejecuta los algoritmos seleccionados de forma unificada para la exportación."""
    results = []
    for alg in alg_list:
        try:
            if alg == 'greedy':
                res = coin_change_greedy(coins_list, amount)
                results.append({
                    'algorithm': 'greedy',
                    'coins_used': res.coins_used,
                    'count': res.count,
                    'optimal': res.optimal,
                })
            elif alg == 'dp':
                res = coin_change_dp(coins_list, amount)
                results.append({
                    'algorithm': 'dp',
                    'coins_used': res.coins_used,
                    'count': res.count,
                    'optimal': res.optimal,
                })
            elif alg == 'backtracking':
                if amount <= 60:
                    res = coin_change_backtracking(coins_list, amount)
                    results.append({
                        'algorithm': 'backtracking',
                        'coins_used': res.coins_used,
                        'count': res.count,
                        'optimal': res.optimal,
                    })
                else:
                    results.append({
                        'algorithm': 'backtracking',
                        'coins_used': [],
                        'count': 0,
                        'optimal': False,
                    })
        except Exception:
            results.append({
                'algorithm': alg,
                'coins_used': [],
                'count': 0,
                'optimal': False,
            })

    # Verificar optimalidad real del Greedy comparando con DP
    greedy_r = next((r for r in results if r['algorithm'] == 'greedy'), None)
    dp_r = next((r for r in results if r['algorithm'] == 'dp'), None)

    if greedy_r:
        if dp_r:
            greedy_r['optimal'] = is_greedy_optimal(
                greedy_r['count'],
                greedy_r['coins_used'],
                dp_r['count'],
                dp_r['coins_used'],
                amount,
            )
        else:
            dp_check = coin_change_dp(coins_list, amount)
            greedy_r['optimal'] = is_greedy_optimal(
                greedy_r['count'],
                greedy_r['coins_used'],
                dp_check.count,
                dp_check.coins_used,
                amount,
            )
    return results


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
                'analysis_url': None,
                'conclusion': None,
            },
        )

    try:
        coins_list = parse_coins(coins)
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
                'analysis_url': None,
                'conclusion': None,
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
            greedy_r['optimal'] = is_greedy_optimal(
                greedy_r['count'],
                greedy_r['coins_used'],
                dp_r['count'],
                dp_r['coins_used'],
                amount,
            )
        else:
            # DP no fue seleccionado — correrlo solo para verificar
            dp_check = coin_change_dp(coins_list, amount)
            greedy_r['optimal'] = is_greedy_optimal(
                greedy_r['count'],
                greedy_r['coins_used'],
                dp_check.count,
                dp_check.coins_used,
                amount,
            )

    # Ordenar resultados: greedy, dp, backtracking
    order = {'greedy': 0, 'dp': 1, 'backtracking': 2}
    results.sort(key=lambda r: order.get(r['algorithm'], 99))
    analysis_url = '/analysis?' + urlencode({
        'coins': ','.join(str(c) for c in coins_list),
        'max_amount': amount,
    })

    conclusion = generar_conclusion(results, amount)

    return templates.TemplateResponse(
        request,
        'result.html',
        {
            'amount': amount,
            'request_coins': coins,
            'results': results,
            'analysis_url': analysis_url,
            'conclusion': conclusion,
            'error': None,
        },
    )


@app.get('/analysis', response_class=HTMLResponse, include_in_schema=False)
async def analysis_page(
    request: Request,
    coins: str | None = None,
    max_amount: int | None = None,
):
    """Página de análisis comparativo (sin datos iniciales).

    Args:
        request: Objeto de petición FastAPI.

    Returns:
        Página HTML con el formulario de análisis.
    """
    return templates.TemplateResponse(
        request,
        'analysis.html',
        build_analysis_context(request, coins=coins, max_amount=max_amount),
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
        coins_list = parse_coins(coins)
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

    analysis_context = build_analysis_context(request, coins=coins, max_amount=max_amount)

    return templates.TemplateResponse(
        request,
        'analysis.html',
        analysis_context,
    )


# ---------------------------------------------------------------------------
# Endpoints de Exportación (CSV y PDF)
# ---------------------------------------------------------------------------

@app.get('/export_csv', response_class=StreamingResponse, include_in_schema=False)
async def export_csv(
    coins: str,
    amount: int,
    algorithms: str,
):
    """Exporta los resultados a formato CSV."""
    try:
        coins_list = parse_coins(coins)
        alg_list = [a.strip() for a in algorithms.split(',') if a.strip()]
        results = obtener_resultados_para_exportar(coins_list, amount, alg_list)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Algoritmo', 'Monedas Usadas', 'Cantidad', 'Óptimo'])

        for r in results:
            name_map = {'greedy': 'Algoritmo Voraz (Greedy)', 'dp': 'Programación Dinámica', 'backtracking': 'Backtracking'}
            name = name_map.get(r['algorithm'], r['algorithm'])
            writer.writerow([
                name,
                ', '.join(map(str, r['coins_used'])) if r['coins_used'] else 'Sin solución',
                r['count'] if r['count'] > 0 else 'Sin solución',
                'Sí' if r['optimal'] else 'No'
            ])

        # Excel on Windows often mis-detects UTF-8. Prepend a BOM so Excel
        # recognises the file as UTF-8 and renders accented characters correctly.
        csv_bytes = output.getvalue().encode('utf-8')
        bom_prefixed = io.BytesIO(b"\xef\xbb\xbf" + csv_bytes)
        return StreamingResponse(
            bom_prefixed,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=coin_change_{amount}.csv",
                "Content-Type": "text/csv; charset=utf-8",
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


@app.get('/export_pdf', response_class=StreamingResponse, include_in_schema=False)
async def export_pdf(
    coins: str,
    amount: int,
    algorithms: str,
):
    """Exporta los resultados a formato PDF."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        coins_list = parse_coins(coins)
        alg_list = [a.strip() for a in algorithms.split(',') if a.strip()]
        results = obtener_resultados_para_exportar(coins_list, amount, alg_list)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            leading=28,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=15
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=15
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=10
        )

        story.append(Paragraph("Reporte de Cambio de Moneda", title_style))
        story.append(Paragraph(f"<b>Denominaciones:</b> {coins}<br/><b>Monto objetivo:</b> {amount}", subtitle_style))
        story.append(Spacer(1, 10))

        data = [['Algoritmo', 'Monedas Usadas', 'Cantidad', 'Óptimo']]
        for r in results:
            name_map = {'greedy': 'Algoritmo Voraz (Greedy)', 'dp': 'Programación Dinámica', 'backtracking': 'Backtracking'}
            name = name_map.get(r['algorithm'], r['algorithm'])
            data.append([
                name,
                ', '.join(map(str, r['coins_used'])) if r['coins_used'] else 'Sin solución',
                r['count'] if r['count'] > 0 else 'Sin solución',
                'Sí' if r['optimal'] else 'No'
            ])

        t = Table(data, colWidths=[150, 220, 80, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f7fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        conclusion_text = generar_conclusion(results, amount)
        if conclusion_text:
            story.append(Paragraph(f"<b>Conclusión:</b> {conclusion_text}", body_style))

        doc.build(story)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=coin_change_{amount}.pdf"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


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
        coins_list = parse_coins(coins)
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
                if amount > 60:
                    results.append({
                        'algorithm': 'backtracking',
                        'coins_used': [],
                        'count': 0,
                        'optimal': False,
                        'time_ms': -1,
                        'error': 'Monto supera el limite seguro para Backtracking.',
                    })
                    continue
                result = coin_change_backtracking(coins_list, amount)
                results.append({
                    'algorithm': 'backtracking',
                    'coins_used': result.coins_used,
                    'count': result.count,
                    'optimal': result.optimal,
                    'time_ms': round((time.perf_counter() - start) * 1000, 4),
                })

        greedy_r = next((r for r in results if r['algorithm'] == 'greedy'), None)
        dp_r = next((r for r in results if r['algorithm'] == 'dp'), None)

        if greedy_r:
            if dp_r:
                greedy_r['optimal'] = is_greedy_optimal(
                    greedy_r['count'],
                    greedy_r['coins_used'],
                    dp_r['count'],
                    dp_r['coins_used'],
                    amount,
                )
            else:
                dp_check = coin_change_dp(coins_list, amount)
                greedy_r['optimal'] = is_greedy_optimal(
                    greedy_r['count'],
                    greedy_r['coins_used'],
                    dp_check.count,
                    dp_check.coins_used,
                    amount,
                )

        order = {'greedy': 0, 'dp': 1, 'backtracking': 2}
        results.sort(key=lambda r: order.get(r['algorithm'], 99))

        return {
            'amount': amount,
            'coins': coins_list,
            'results': results,
        }

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={'error': str(e)},
        )
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