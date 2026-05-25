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
    """Ejecuta los algoritmos seleccionados y muestra los resultados."""
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
                    'steps': result.steps,
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
    """Página de análisis comparativo (sin datos iniciales)."""
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
    """Ejecuta el análisis comparativo y muestra resultados con gráficos."""
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
# Endpoints de Exportación de Análisis (CSV y PDF)
# ---------------------------------------------------------------------------

@app.get('/export_analysis_csv', response_class=StreamingResponse, include_in_schema=False)
async def export_analysis_csv(
    coins: str,
    max_amount: int = 200,
):
    """Exporta la tabla completa del análisis comparativo a CSV."""
    try:
        coins_list = parse_coins(coins)
        analysis_result = run_analysis(coins_list, max_amount)
        points = analysis_result.get('points', [])

        pivot: dict[int, dict] = {}
        for p in points:
            amt = p['amount']
            alg = p['algorithm']
            if amt not in pivot:
                pivot[amt] = {}
            pivot[amt][alg] = p

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Monto',
            'Tiempo Greedy (ms)', 'Tiempo DP (ms)', 'Tiempo Backtracking (ms)',
            'Monedas Greedy', 'Monedas DP', 'Monedas Backtracking',
            'Memoria Greedy (KB)', 'Memoria DP (KB)', 'Memoria Backtracking (KB)',
            'Brecha Greedy vs DP',
        ])
        for amt in sorted(pivot):
            row_data = pivot[amt]
            g = row_data.get('greedy', {})
            d = row_data.get('dp', {})
            bt = row_data.get('backtracking', {})
            greedy_coins = g.get('coins_used', '')
            dp_coins = d.get('coins_used', '')
            gap = (greedy_coins - dp_coins) if isinstance(greedy_coins, int) and isinstance(dp_coins, int) and greedy_coins >= 0 and dp_coins >= 0 else ''
            writer.writerow([
                amt,
                round(g.get('time_ms', ''), 4) if g else '',
                round(d.get('time_ms', ''), 4) if d else '',
                round(bt.get('time_ms', ''), 4) if bt else '',
                greedy_coins if isinstance(greedy_coins, int) and greedy_coins >= 0 else '',
                dp_coins if isinstance(dp_coins, int) and dp_coins >= 0 else '',
                bt.get('coins_used', '') if isinstance(bt.get('coins_used'), int) and bt.get('coins_used', -1) >= 0 else '',
                round(g.get('memory_kb', ''), 4) if g else '',
                round(d.get('memory_kb', ''), 4) if d else '',
                round(bt.get('memory_kb', ''), 4) if bt else '',
                gap,
            ])

        csv_bytes = output.getvalue().encode('utf-8')
        bom_prefixed = io.BytesIO(b"\xef\xbb\xbf" + csv_bytes)
        return StreamingResponse(
            bom_prefixed,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename=analisis_coins_{max_amount}.csv",
                "Content-Type": "text/csv; charset=utf-8",
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})


@app.get('/export_analysis_pdf', response_class=StreamingResponse, include_in_schema=False)
async def export_analysis_pdf(
    coins: str,
    max_amount: int = 200,
):
    """Exporta el análisis comparativo a PDF incluyendo gráficas y tablas de datos corregidas."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        coins_list = parse_coins(coins)
        analysis_result = run_analysis(coins_list, max_amount)
        points = analysis_result.get('points', [])
        summary = analysis_result.get('summary', {})
        complexity_table = analysis_result.get('complexity_table', [])
        greedy_gap_summary = analysis_result.get('greedy_gap_summary', {})

        graph_paths = [
            analysis_result.get('graph_path'),
            analysis_result.get('coins_used_graph_path'),
            analysis_result.get('memory_graph_path'),
            analysis_result.get('greedy_gap_graph_path'),
        ]
        graph_labels = [
            'Tiempo de ejecución vs Monto',
            'Cantidad de monedas usadas vs Monto',
            'Memoria pico vs Monto',
            'Brecha Greedy vs DP',
        ]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'],
            fontSize=22, leading=26, textColor=colors.HexColor('#1a365d'), spaceAfter=6,
        )
        section_style = ParagraphStyle(
            'SectionStyle', parent=styles['Heading2'],
            fontSize=14, leading=18, textColor=colors.HexColor('#2b6cb0'), spaceAfter=6, spaceBefore=14,
        )
        body_style = ParagraphStyle(
            'BodyStyle', parent=styles['Normal'],
            fontSize=9, leading=13, textColor=colors.HexColor('#2d3748'), spaceAfter=6,
        )
        small_style = ParagraphStyle(
            'SmallStyle', parent=styles['Normal'],
            fontSize=8, leading=11, textColor=colors.HexColor('#4a5568'),
        )

        # Título
        story.append(Paragraph("Análisis Comparativo — Cambio de Moneda", title_style))
        story.append(Paragraph(
            f"<b>Denominaciones:</b> {coins} &nbsp;&nbsp; <b>Monto máximo:</b> {max_amount}",
            body_style,
        ))
        story.append(Spacer(1, 10))

        # Tabla de complejidad
        if complexity_table:
            story.append(Paragraph("Complejidad Algorítmica", section_style))
            note_style = ParagraphStyle(
                'NoteStyle', parent=styles['Normal'],
                fontSize=8, leading=11, textColor=colors.HexColor('#2d3748'),
            )
            header = ['Algoritmo', 'Tiempo', 'Espacio', 'Óptimo', 'Nota']
            rows = [header]
            for row in complexity_table:
                rows.append([
                    str(row.get('algorithm', '')),
                    str(row.get('time_complexity', '')),
                    str(row.get('space_complexity', '')),
                    str(row.get('guarantees_optimal', '')),
                    Paragraph(str(row.get('note', '')), note_style),
                ])
            col_widths = [110, 80, 75, 50, 215]
            t = Table(rows, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-2, -1), 'CENTER'),
                ('ALIGN', (4, 1), (4, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#edf2f7')]),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))

        # Resumen (Manejo correcto de 'averages')
        if summary:
            story.append(Paragraph("Resumen del Análisis", section_style))
            for key, val in summary.items():
                if key == 'averages' and isinstance(val, list):
                    story.append(Paragraph("<b>Rendimiento Promedio General:</b>", body_style))
                    story.append(Spacer(1, 4))
                    
                    avg_headers = ['Algoritmo', 'Tiempo Promedio (ms)', 'Memoria Promedio (KB)']
                    avg_rows = [avg_headers]
                    
                    for item in val:
                        avg_rows.append([
                            str(item.get('algorithm', '')),
                            f"{item.get('avg_time_ms', 0.0):.6f}",
                            f"{item.get('avg_memory_kb', 0.0):.4f}"
                        ])
                    
                    avg_table = Table(avg_rows, colWidths=[180, 175, 175])
                    avg_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e0')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
                        ('PADDING', (0, 0), (-1, -1), 5),
                    ]))
                    story.append(avg_table)
                    story.append(Spacer(1, 8))
                else:
                    story.append(Paragraph(f"<b>{key}:</b> {val}", body_style))
            story.append(Spacer(1, 6))

        # Brecha Greedy (Manejo estructurado de 'failures' y 'first_failure')
        if greedy_gap_summary:
            story.append(Paragraph("Brecha Greedy vs DP", section_style))
            for key, val in greedy_gap_summary.items():
                if key == 'failures' and isinstance(val, list):
                    if not val:
                        story.append(Paragraph("<b>Casos de Fallo (Subóptimos):</b> Ninguno. ¡El algoritmo voraz fue óptimo en todo el rango!", body_style))
                    else:
                        story.append(Paragraph(f"<b>Casos de Fallo ({len(val)} montos subóptimos):</b>", body_style))
                        story.append(Spacer(1, 4))
                        
                        # Generar tabla para listar los montos con diferencias (primeros 5 para no saturar)
                        fail_headers = ['Monto Objetivo', 'Monedas Greedy', 'Monedas DP (Óptimo)', 'Diferencia (Brecha)']
                        fail_rows = [fail_headers]
                        
                        for item in val[:5]:
                            fail_rows.append([
                                str(item.get('amount', '')),
                                str(item.get('greedy_count', '')),
                                str(item.get('dp_count', '')),
                                f"+{item.get('gap', 0)}"
                            ])
                        
                        if len(val) > 5:
                            fail_rows.append([f"... y {len(val) - 5} casos más", "", "", ""])

                        fail_table = Table(fail_rows, colWidths=[130, 130, 140, 130])
                        fail_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b2c2c')),  # Tono rojizo para fallos
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#fed7d7')),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
                            ('PADDING', (0, 0), (-1, -1), 5),
                        ]))
                        story.append(fail_table)
                        story.append(Spacer(1, 8))

                elif key == 'first_failure' and isinstance(val, dict):
                    if val:
                        txt = f"Monto {val.get('amount')} (Voraz: {val.get('greedy_count')} mon. vs DP: {val.get('dp_count')} mon.)"
                        story.append(Paragraph(f"<b>Primer caso subóptimo detectado:</b> {txt}", body_style))
                    else:
                        story.append(Paragraph("<b>Primer caso subóptimo detectado:</b> N/A", body_style))
                else:
                    # Muestra de manera limpia campos planos como failure_count, max_gap y total_extra_coins
                    story.append(Paragraph(f"<b>{key}:</b> {val}", body_style))
            story.append(Spacer(1, 6))

        # Gráficas
        story.append(Paragraph("Gráficas Comparativas", section_style))
        for label, gpath in zip(graph_labels, graph_paths):
            if gpath:
                full_path = BASE_DIR / gpath.lstrip('/')
                if full_path.exists():
                    story.append(Paragraph(label, small_style))
                    story.append(Spacer(1, 4))
                    img = RLImage(str(full_path), width=6.5 * inch, height=3.2 * inch)
                    story.append(img)
                    story.append(Spacer(1, 10))

        # Tabla de datos (primeras 100 filas)
        if points:
            story.append(Paragraph("Tabla de Datos (primeros 100 montos)", section_style))
            header_row = ['Monto', 'T.Greedy(ms)', 'T.DP(ms)', 'T.BT(ms)',
                          'N.Greedy', 'N.DP', 'N.BT', 'Brecha']
            rows = [header_row]

            pivot_pdf: dict[int, dict] = {}
            for p in points:
                amt = p['amount']
                alg = p['algorithm']
                if amt not in pivot_pdf:
                    pivot_pdf[amt] = {}
                pivot_pdf[amt][alg] = p

            def fmt(v):
                if v is None or v == '':
                    return '—'
                if isinstance(v, float):
                    return f"{v:.4f}"
                return str(v)

            for amt in sorted(pivot_pdf)[:100]:
                row_data = pivot_pdf[amt]
                g = row_data.get('greedy', {})
                d = row_data.get('dp', {})
                bt = row_data.get('backtracking', {})
                g_coins = g.get('coins_used', -1)
                d_coins = d.get('coins_used', -1)
                gap = (g_coins - d_coins) if isinstance(g_coins, int) and isinstance(d_coins, int) and g_coins >= 0 and d_coins >= 0 else None
                rows.append([
                    fmt(amt),
                    fmt(g.get('time_ms')) if g else '—',
                    fmt(d.get('time_ms')) if d else '—',
                    fmt(bt.get('time_ms')) if bt else '—',
                    fmt(g_coins if g_coins >= 0 else None) if g else '—',
                    fmt(d_coins if d_coins >= 0 else None) if d else '—',
                    fmt(bt.get('coins_used') if isinstance(bt.get('coins_used'), int) and bt.get('coins_used', -1) >= 0 else None) if bt else '—',
                    fmt(gap),
                ])
            col_w = [45, 72, 60, 60, 55, 45, 45, 50]
            t2 = Table(rows, colWidths=col_w, repeatRows=1)
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#edf2f7')]),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(t2)

        doc.build(story)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=analisis_coins_{max_amount}.pdf"},
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
    """Endpoint REST que resuelve el cambio de moneda y retorna JSON."""
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