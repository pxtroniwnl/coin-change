# Coin Change — Problema del Cambio de Moneda

Aplicación web interactiva que resuelve el problema clásico del cambio de moneda usando **tres paradigmas algorítmicos diferentes**, con visualización de resultados y análisis comparativo de rendimiento.

> **Proyecto Final · Algoritmo y Complejidad · 2026**  
> Shalom Jhoanna Arrieta Marrugo · Alejandro Patron Montero · Dariem Garcia Cardona · Dayana Narvaez · Lineth Villalba

---

## Descripción del problema

Dado un conjunto de denominaciones de monedas y un monto objetivo, encontrar la **mínima cantidad de monedas** necesarias para formar ese monto exacto.

```
Monedas:  [1, 5, 6]
Monto:    11

Solución voraz:   5 + 5 + 1  →  3 monedas  (no óptima)
Solución óptima:  6 + 5      →  2 monedas
```

Este problema es especialmente interesante porque ilustra cómo distintos enfoques algorítmicos pueden producir resultados de diferente calidad y eficiencia sobre el mismo problema.

---

## Requisitos previos

Antes de instalar el proyecto, asegúrate de tener instalado:

- **Python 3.10 o superior** — [Descargar aquí](https://www.python.org/downloads/)
- **pip** — Viene incluido con Python (verifica con `pip --version`)
- **git** — Para clonar el repositorio

Para verificar tu versión de Python:

```bash
python --version
# o en algunos sistemas:
python3 --version
```

> En Windows, si tienes ambos `python` y `python3`, usa el que apunte a la versión 3.10+.

---

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd coin-change
```

### 2. Crear un entorno virtual

Un entorno virtual aísla las dependencias del proyecto para no afectar tu instalación de Python global.

```bash
# Linux / macOS
python3 -m venv venv

# Windows
python -m venv venv
```

### 3. Activar el entorno virtual

Este paso es **obligatorio** cada vez que abras una nueva terminal para trabajar con el proyecto.

```bash
# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

Sabrás que el entorno está activo cuando veas `(venv)` al inicio de tu línea de comando:

```
(venv) usuario@equipo:~/coin-change$
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala automáticamente: FastAPI, Uvicorn, Jinja2, Matplotlib, Pydantic y Pytest.

---

## Ejecutar la aplicación

Con el entorno virtual activado, ejecuta uno de los siguientes comandos:

```bash
# Opción 1 (recomendada en desarrollo — recarga automáticamente al guardar cambios)
uvicorn app:app --reload

# Opción 2 (directa)
python app.py
```

Luego abre tu navegador en:

```
http://localhost:8000
```

Para detener el servidor, presiona `Ctrl + C` en la terminal.

---

## Cómo usar la aplicación

### Página principal — Resolver (`/`)

1. **Sistema de monedas predefinido** — Selecciona uno de los sistemas incluidos (USD, EUR, COP, o sistemas no canónicos) para cargarlo automáticamente.
2. **Denominaciones personalizadas** — Escribe tus propias denominaciones separadas por coma (ej: `1,5,10,25`).
3. **Monto objetivo** — Ingresa el valor que quieres formar.
4. **Algoritmos** — Marca cuáles algoritmos quieres ejecutar (puedes seleccionar uno, dos o los tres).
5. Haz clic en **Resolver** para ver los resultados.

> **Nota:** El backtracking en esta página está limitado a montos ≤ 60. Si ingresas un monto mayor con backtracking activado, se mostrará un mensaje de error explicativo y los demás algoritmos seguirán funcionando con normalidad.

**En la página de resultados** podrás ver para cada algoritmo:
- Las monedas utilizadas (mostradas como chips visuales)
- La cantidad total de monedas
- El tiempo de ejecución en milisegundos
- Si la solución es óptima o no
- Detalles expandibles: pasos del Greedy, tabla completa de DP, o estadísticas del Backtracking

### Página de Análisis (`/analysis`)

1. Ingresa las denominaciones y el monto máximo a evaluar.
2. Haz clic en **Ejecutar análisis**.
3. La aplicación correrá los tres algoritmos para todos los montos desde 0 hasta el máximo elegido.
4. Se generan tres gráficos comparativos:
   - **Tiempo de ejecución vs. Monto** — para comparar velocidad
   - **Cantidad de monedas vs. Monto** — para comparar calidad de solución
   - **Memoria pico vs. Monto** — para comparar uso de memoria RAM real (medido con `tracemalloc`)
5. También verás la tabla completa de datos (tiempo, monedas usadas y memoria pico en KB) y las conclusiones del análisis.

> **Nota:** El backtracking se limita automáticamente a montos ≤ 60 para evitar tiempos de espera excesivos.

### API REST (`/api/solve`)

También puedes consultar los algoritmos directamente vía HTTP:

```bash
# Resolver con monedas [1,5,6] para monto 11 usando greedy y DP
curl "http://localhost:8000/api/solve?coins=1,5,6&amount=11&algorithms=greedy,dp"
```

Respuesta:

```json
{
  "amount": 11,
  "coins": [1, 5, 6],
  "results": [
    {
      "algorithm": "greedy",
      "coins_used": [5, 5, 1],
      "count": 3,
      "optimal": false,
      "time_ms": 0.0123
    },
    {
      "algorithm": "dp",
      "coins_used": [5, 6],
      "count": 2,
      "optimal": true,
      "time_ms": 0.0456
    }
  ]
}
```

**Parámetros:**

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `coins` | string | Denominaciones separadas por coma | `1,5,10,25` |
| `amount` | entero | Monto objetivo | `47` |
| `algorithms` | string | Algoritmos separados por coma (opcional, default: todos) | `greedy,dp` |

---

## Ejecutar los tests

```bash
# Todos los tests con detalle
python -m pytest tests/ -v

# Solo greedy
python -m pytest tests/test_greedy.py -v

# Solo programación dinámica
python -m pytest tests/test_dynamic_programming.py -v

# Solo backtracking
python -m pytest tests/test_backtracking.py -v
```

---

## Algoritmos implementados

### 1. Algoritmo Voraz (Greedy) — `src/greedy.py`

Selecciona siempre la moneda de mayor denominación que no supere el monto restante, repitiendo hasta cubrir el monto completo.

```
Complejidad temporal:  O(n)   donde n = número de denominaciones
Complejidad espacial:  O(1)
Solución óptima:       No garantizada (falla en sistemas no canónicos)
```

**Cuándo falla:** El Greedy falla cuando elegir la moneda más grande bloquea combinaciones más eficientes. Ejemplos concretos con los sistemas no canónicos incluidos:

- `[1, 5, 6]` con monto `10` → Greedy: `6+1+1+1+1` = 5 monedas · Óptimo: `5+5` = 2 monedas
- `[1, 3, 4]` con monto `6` → Greedy: `4+1+1` = 3 monedas · Óptimo: `3+3` = 2 monedas
- `[1, 12, 20, 25]` con monto `40` → Greedy: `25+12+1+1+1` = 5 monedas · Óptimo: `20+20` = 2 monedas

### 2. Programación Dinámica (Bottom-Up) — `src/dynamic_programming.py`

Construye una tabla `dp[]` donde `dp[i]` = mínima cantidad de monedas para el monto `i`. Evalúa cada subproblema una sola vez y luego reconstruye la solución recorriendo la tabla hacia atrás.

```
Complejidad temporal:  O(m × n)   donde m = monto, n = denominaciones
Complejidad espacial:  O(m)       arreglo dp[] de tamaño (monto + 1)
Solución óptima:       Siempre garantizada
```

### 3. Backtracking con poda — `src/backtracking.py`

Explora recursivamente todas las combinaciones posibles de monedas. Utiliza poda: descarta ramas que ya usan más monedas que la mejor solución encontrada hasta el momento.

```
Complejidad temporal:  O(2ⁿ) en el peor caso
Complejidad espacial:  O(profundidad)  pila de recursión
Solución óptima:       Siempre garantizada
Límite práctico:       Montos ≤ 60
```

---

## Comparativa de los tres enfoques

| Aspecto | Voraz (Greedy) | Programación Dinámica | Backtracking |
|---------|---------------|----------------------|--------------|
| **Velocidad** | Más rápido | Rápido | Muy lento |
| **Memoria** | O(1) · constante | O(m) · arreglo dp[] | O(prof.) · pila recursión |
| **Siempre óptimo** | No | Sí | Sí |
| **Escala bien** | Sí | Sí | No (montos grandes) |
| **Recomendado para** | Sistemas canónicos, tiempo crítico | Uso general | Fines educativos |

**Conclusión esperada:** El Greedy es el más rápido y usa mínima memoria, pero puede fallar en sistemas no canónicos. La Programación Dinámica es la solución más robusta para uso general, aunque usa más memoria al mantener el arreglo `dp[]` completo. El Backtracking garantiza el óptimo explorando todas las combinaciones, pero su costo exponencial en tiempo y su pila de recursión lo hacen inviable para montos grandes.

---

## Estructura del proyecto

```
coin-change/
├── app.py                      # Servidor FastAPI — todos los endpoints
├── requirements.txt            # Dependencias Python
│
├── src/                        # Implementaciones de los algoritmos
│   ├── coins.py                # Sistemas de monedas predefinidos (USD, EUR, COP, etc.)
│   ├── schemas.py              # Modelos Pydantic (validación de datos)
│   ├── greedy.py               # Algoritmo Voraz → GreedyResult
│   ├── dynamic_programming.py  # Programación Dinámica → DPResult
│   ├── backtracking.py         # Backtracking → BacktrackingResult
│   └── analysis.py             # Benchmarking, medición de memoria y generación de gráficos
│
├── templates/                  # Plantillas HTML (Jinja2)
│   ├── base.html               # Estructura base: navbar, footer, fuentes
│   ├── index.html              # Formulario principal y descripción de algoritmos
│   ├── result.html             # Visualización de resultados por algoritmo
│   └── analysis.html           # Gráficos y tabla del análisis comparativo
│
├── static/
│   ├── css/style.css           # Todos los estilos (tema dark indie)
│   └── graphs/                 # Gráficos PNG generados por Matplotlib
│       ├── time_analysis.png       # Tiempo de ejecución vs Monto
│       ├── coins_analysis.png      # Cantidad de monedas vs Monto
│       └── memory_analysis.png     # Memoria pico vs Monto
│
└── tests/                      # Tests unitarios con Pytest
    ├── test_greedy.py
    ├── test_dynamic_programming.py
    └── test_backtracking.py
```

---

## Sistemas de monedas incluidos

La aplicación incluye estos sistemas predefinidos:

| Sistema | Denominaciones | Tipo | Greedy falla en |
|---------|---------------|------|-----------------|
| USD (Dólar) | 1, 5, 10, 25, 50 | Canónico | — |
| EUR (Euro) | 1, 2, 5, 10, 20, 50, 100, 200 | Canónico | — |
| COP (Peso colombiano) | 50, 100, 200, 500, 1000 | Canónico | — |
| No canónico #1 | 1, 5, 6 | No canónico | monto `10` → da 5 monedas, óptimo 2 |
| No canónico #2 | 1, 3, 4 | No canónico | monto `6` → da 3 monedas, óptimo 2 |
| No canónico #3 | 1, 12, 20, 25 | No canónico | monto `40` → da 5 monedas, óptimo 2 |

Los sistemas **no canónicos** son los más interesantes para el análisis porque demuestran dónde falla el algoritmo Greedy.

---

## Solución de problemas comunes

**`command not found: uvicorn`**  
El entorno virtual no está activado. Ejecuta `source venv/bin/activate` (Linux/macOS) o `venv\Scripts\activate` (Windows) y vuelve a intentarlo.

**`ModuleNotFoundError`**  
Las dependencias no están instaladas en el entorno activo. Asegúrate de activar el entorno virtual y luego ejecuta `pip install -r requirements.txt`.

**Error de Python en Windows: `python` no encontrado**  
Usa `python3` en lugar de `python`, o verifica que Python esté en el PATH del sistema.

**Los gráficos no se muestran después del análisis**  
Asegúrate de que el directorio `static/graphs/` exista. Puedes crearlo manualmente: `mkdir -p static/graphs`.

**El backtracking tarda demasiado o muestra error de límite**  
Es normal para montos mayores a 60. La página de análisis y la página principal limitan backtracking a ≤ 60 automáticamente. Para montos grandes usa Programación Dinámica.

---

## Tecnologías

- **Python 3.10+** — Lenguaje principal
- **FastAPI** — Framework web (endpoints HTML y API REST)
- **Uvicorn** — Servidor ASGI
- **Jinja2** — Motor de plantillas HTML
- **Pydantic v2** — Validación y serialización de datos
- **Matplotlib** — Generación de gráficos de benchmarking
- **tracemalloc** — Medición de uso de memoria en tiempo de ejecución (stdlib)
- **Pytest** — Tests unitarios
- **Google Fonts** — Tipografías: Syne, JetBrains Mono, Inter