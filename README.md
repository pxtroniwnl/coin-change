# Coin Change — Problema del Cambio de Moneda

Aplicación web interactiva hecha con **FastAPI** para resolver el problema clásico del cambio de moneda usando tres paradigmas algorítmicos distintos: **Greedy**, **Programación Dinámica** y **Backtracking con poda**.

> **Proyecto Final — Algoritmos y Complejidad — 2026**

---

## Integrantes

| Nombre | Rol |
|---|---|
| Shalom Jhoanna Arrieta Marrugo | Desarrollo y documentación |
| Alejandro Patron Montero | Desarrollo y documentación |
| Dariem Garcia Cardona | Desarrollo y documentación |
| Dayana Narvaez | Desarrollo y documentación |
| Lineth Villalba | Desarrollo y documentación |

---

## Tabla de contenido

1. [El problema del cambio de moneda](#1-el-problema-del-cambio-de-moneda)
2. [Lógica detrás de cada algoritmo](#2-lógica-detrás-de-cada-algoritmo)
3. [Instalación y ejecución con uv](#3-instalación-y-ejecución-con-uv)
4. [Instalación alternativa con pip](#4-instalación-alternativa-con-pip)
5. [Cómo usar la aplicación](#5-cómo-usar-la-aplicación)
6. [API REST](#6-api-rest)
7. [Tests y resultados](#7-tests-y-resultados)
8. [Estructura del proyecto](#8-estructura-del-proyecto)
9. [Sistemas de monedas incluidos](#9-sistemas-de-monedas-incluidos)
10. [Tecnologías](#10-tecnologías)
11. [Solución de problemas comunes](#11-solución-de-problemas-comunes)

---

## 1. El problema del cambio de moneda

### Definición formal

Dado un conjunto de denominaciones de monedas `C = {c₁, c₂, ..., cₙ}` y un monto objetivo `m`, se quiere encontrar la **combinación de monedas con repetición** que sume exactamente `m` usando la **menor cantidad posible de monedas**.

```
Minimizar:  Σ xᵢ
Sujeto a:   Σ cᵢ · xᵢ = m
            xᵢ ≥ 0, xᵢ ∈ ℤ
```

Donde `xᵢ` es el número de veces que se usa la moneda `cᵢ`.

### ¿Por qué es un problema interesante?

A primera vista parece simple: tomar siempre la moneda más grande posible. Sin embargo, esa estrategia (Greedy) **no siempre produce la solución óptima**.

#### Ejemplo donde Greedy falla

```
Monedas disponibles: [1, 5, 6]
Monto objetivo:       10

Greedy (más grande primero):
  Toma 6  → resta 4
  Toma 1  → resta 3
  Toma 1  → resta 2
  Toma 1  → resta 1
  Toma 1  → resta 0
  Total: 5 monedas   ← subóptimo

Solución óptima:
  Toma 5  → resta 5
  Toma 5  → resta 0
  Total: 2 monedas   ← óptimo
```

Esto ocurre porque el problema tiene **subestructura óptima** y **solapamiento de subproblemas**, dos características que lo convierten en un candidato clásico para Programación Dinámica.

#### Otros casos donde Greedy falla

```
Monedas: [1, 3, 4]   Monto: 6
  Greedy: 4 + 1 + 1 = 3 monedas
  Óptimo: 3 + 3     = 2 monedas

Monedas: [1, 12, 20, 25]   Monto: 40
  Greedy: 25 + 12 + 1 + 1 + 1 = 5 monedas
  Óptimo: 20 + 20             = 2 monedas
```

### Casos especiales

- **Monto 0:** La solución siempre es cero monedas, independientemente del sistema.
- **Sin solución:** Si ninguna combinación puede formar el monto (por ejemplo, monedas `[2]` y monto `3`), el resultado es vacío.
- **Sistemas canónicos:** Para monedas del mundo real como USD o EUR, Greedy siempre encuentra el óptimo porque sus denominaciones están diseñadas para eso.

---

## 2. Lógica detrás de cada algoritmo

### 2.1 Greedy (Voraz) — `src/greedy.py`

**Idea central:** elegir en cada paso la moneda más grande posible que no supere el monto restante, sin revisar las consecuencias futuras de esa elección.

**Cómo funciona paso a paso:**

```
Ordenar monedas de mayor a menor: [c_n, c_{n-1}, ..., c_1]
restante = monto
Para cada moneda c en orden descendente:
    mientras c <= restante:
        tomar c
        restante -= c
```

**Ejemplo visual con [1, 5, 6], monto 11:**

```
Paso 1: mayor moneda disponible = 6 ≤ 11 → tomar 6   (restante: 5)
Paso 2: mayor moneda disponible = 6 > 5  → saltar
         siguiente = 5 ≤ 5  → tomar 5   (restante: 0)
Resultado: [6, 5] → 2 monedas (óptimo en este caso)
```

**Complejidad:**

| Aspecto | Valor |
|---|---|
| Tiempo | O(n · k) donde k = monedas usadas |
| Espacio | O(1) auxiliar |
| Óptimo garantizado | No |

**Verificación de optimalidad:** El módulo Greedy nunca determina su propia optimalidad. La aplicación siempre corre DP en silencio y compara el conteo. Si `greedy_count == dp_count`, se marca como óptimo.

---

### 2.2 Programación Dinámica — `src/dynamic_programming.py`

**Idea central:** resolver el problema descomponiéndolo en subproblemas más pequeños y almacenar sus soluciones para no recalcularlos (memoización bottom-up).

**Propiedad de subestructura óptima:**

```
dp[0] = 0
dp[i] = min{ dp[i - c] + 1 }  para todo c en monedas donde c ≤ i
dp[i] = ∞  si ninguna moneda puede llegar a i
```

La solución al monto `m` se construye revisando cada monto intermedio de `1` hasta `m`, y para cada uno probando todas las monedas disponibles.

**Ejemplo con [1, 5, 6], monto 10:**

```
dp[0] = 0
dp[1] = dp[0] + 1 = 1       (usando moneda 1)
dp[2] = dp[1] + 1 = 2       (usando moneda 1)
dp[3] = dp[2] + 1 = 3       (usando moneda 1)
dp[4] = dp[3] + 1 = 4       (usando moneda 1)
dp[5] = min(dp[4]+1, dp[0]+1) = 1    (usando moneda 5)
dp[6] = min(dp[5]+1, dp[1]+1, dp[0]+1) = 1   (usando moneda 6)
dp[7] = min(dp[6]+1, dp[2]+1, dp[1]+1) = 2   (6+1 o 5+1+1)
dp[8] = 3
dp[9] = 2   (usando 5+4? No... 6+3? No... mejor: dp[3]+1=4, dp[4]+1=5... realmente dp[3]+1, dp[8]+1... )
     = min(dp[8]+1=4, dp[4]+1=5, dp[3]+1=4) → pero [5,5]... dp[5]+1 con moneda 5 = 2
dp[10] = min(dp[9]+1, dp[5]+1, dp[4]+1) = min(3, 2, 5) = 2  (usando 5+5)
```

Para reconstruir las monedas usadas, se guarda qué moneda se eligió en cada posición y se traza hacia atrás desde `dp[m]`.

**Complejidad:**

| Aspecto | Valor |
|---|---|
| Tiempo | O(m × n) donde m = monto, n = número de denominaciones |
| Espacio | O(m) para la tabla dp |
| Óptimo garantizado | Sí, siempre |

---

### 2.3 Backtracking con poda — `src/backtracking.py`

**Idea central:** explorar todas las combinaciones posibles de monedas de forma recursiva, pero descartar (podar) ramas del árbol de búsqueda que no pueden mejorar la mejor solución encontrada hasta el momento.

**Árbol de búsqueda (ejemplo con [1, 5, 6], monto 10):**

```
                    monto=10
                  /    |    \
              -6       -5    -1
           monto=4   monto=5  monto=9
          / | \      / | \    ...
        -6 -5 -1  -6 -5 -1
        (>4) m=0  m=4   ...
             
             [6,5]=2 → mejor hasta ahora = 2
             → podar cualquier rama con ≥ 2 monedas usadas
```

La poda funciona así: si el número de monedas ya tomadas supera o iguala el mejor resultado conocido, se abandona esa rama sin explorarla más.

**Complejidad:**

| Aspecto | Valor |
|---|---|
| Tiempo | Exponencial en el peor caso |
| Espacio | O(profundidad del árbol) |
| Óptimo garantizado | Sí |
| Límite práctico | Montos ≤ 60 |

El límite de 60 está impuesto en la aplicación porque para montos mayores el árbol de búsqueda crece de forma inmanejable, incluso con poda.

---

### 2.4 Comparación general

| Aspecto | Greedy | Programación Dinámica | Backtracking |
|---|---|---|---|
| Paradigma | Voraz (decisión local) | Bottom-up (subproblemas) | Búsqueda exhaustiva con poda |
| Complejidad tiempo | O(n · k) | O(m × n) | Exponencial |
| Complejidad espacio | O(1) | O(m) | O(profundidad) |
| Garantiza óptimo | No | Sí | Sí |
| Escala a montos grandes | Sí | Sí | No (límite = 60) |
| Cuándo usarlo | Sistemas canónicos o velocidad crítica | Uso general | Estudio académico / montos pequeños |

**Conclusión:** Para uso práctico, **Programación Dinámica** es la mejor opción. Greedy es más rápido pero puede fallar. Backtracking es el más didáctico para entender la estructura del problema, pero inviable para montos grandes.

---

## 3. Instalación y ejecución con uv

[`uv`](https://docs.astral.sh/uv/) es un gestor de paquetes y entornos virtuales para Python escrito en Rust, significativamente más rápido que `pip`. Es el método recomendado para este proyecto.

### 3.1 Instalar uv

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verifica la instalación:
```bash
uv --version
```

### 3.2 Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd coin-change
```

### 3.3 Crear entorno virtual e instalar dependencias

`uv` detecta automáticamente `requirements.txt` y crea el entorno virtual en `.venv/`:

```bash
uv sync --requirements requirements.txt
```

O si prefieres especificar la versión de Python:

```bash
uv sync --python 3.11 --requirements requirements.txt
```

### 3.4 Ejecutar la aplicación

```bash
uv run uvicorn app:app --reload
```

O directamente:

```bash
uv run python app.py
```

Luego abre en tu navegador:

```
http://localhost:8000
```

Para detener el servidor presiona `Ctrl + C`.

### 3.5 Ejecutar los tests con uv

```bash
uv run python -m pytest tests -q
```

Para ver detalle por archivo:

```bash
uv run python -m pytest tests/test_greedy.py -v
uv run python -m pytest tests/test_dynamic_programming.py -v
uv run python -m pytest tests/test_backtracking.py -v
```

---

## 4. Instalación alternativa con pip

Si prefieres no usar `uv`, puedes usar el flujo clásico con `pip`.

### Requisitos

- Python 3.10 o superior
- pip
- git

### Pasos

```bash
# 1. Clonar
git clone <url-del-repositorio>
cd coin-change

# 2. Crear entorno virtual
python -m venv venv          # Linux/macOS
python3 -m venv venv         # En algunos sistemas

# 3. Activar entorno virtual
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate.bat    # Windows CMD
venv\Scripts\Activate.ps1    # Windows PowerShell

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
uvicorn app:app --reload
```

> Si desea generar reportes en PDF desde la aplicación o los endpoints de análisis, asegúrese de tener instalada la dependencia `reportlab`.


---

## 5. Cómo usar la aplicación

### Flujo principal

1. Abre `http://localhost:8000`.
2. Selecciona un sistema de monedas predefinido o escribe denominaciones personalizadas separadas por coma (ej: `1,5,6`).
3. Ingresa el monto objetivo (ej: `25`).
4. Marca los algoritmos que quieres ejecutar.
5. Haz clic en **Resolver**.
6. Revisa los resultados por algoritmo: monedas usadas, cantidad, optimality, tiempo.
7. Haz clic en **Ver análisis** para ir a la página de benchmarks con los mismos parámetros prellenados.

### Página de resultados (`POST /solve`)

Muestra por cada algoritmo seleccionado:
- Monedas utilizadas y cantidad total.
- Tiempo de ejecución en milisegundos.
- Indicador de optimalidad (verificado siempre contra DP, nunca solo desde Greedy).
- Detalle interno: pasos del Greedy, tabla DP o nodos explorados por Backtracking.

### Página de análisis (`/analysis`)

Genera cuatro gráficas comparativas ejecutando los tres algoritmos sobre todos los montos de `1` a `max_amount`:

- **Tiempo de ejecución vs monto** — muestra cuándo Backtracking se vuelve inviable.
- **Memoria pico vs monto** — medida con `tracemalloc`.
- **Cantidad de monedas usadas vs monto** — muestra la brecha entre Greedy y el óptimo.
- **Brecha Greedy vs DP** — cuántas monedas de más usa Greedy cuando falla.

También genera:
- Tabla de complejidad algorítmica.
- Resumen con el algoritmo más rápido, menor memoria y recomendado para uso general.
- Tabla completa de datos por monto.

---

## 6. API REST

El endpoint `GET /api/solve` permite resolver casos directamente desde HTTP sin usar la interfaz web.

```bash
curl "http://localhost:8000/api/solve?coins=1,5,6&amount=10&algorithms=greedy,dp"
```

**Respuesta:**

```json
{
  "amount": 10,
  "coins": [1, 5, 6],
  "results": [
    {
      "algorithm": "greedy",
      "coins_used": [6, 1, 1, 1, 1],
      "count": 5,
      "optimal": false,
      "time_ms": 0.0123
    },
    {
      "algorithm": "dp",
      "coins_used": [5, 5],
      "count": 2,
      "optimal": true,
      "time_ms": 0.0456
    }
  ]
}
```

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `coins` | string | Sí | Denominaciones separadas por coma, ej: `1,5,10,25` |
| `amount` | entero | Sí | Monto objetivo no negativo |
| `algorithms` | string | No | Algoritmos separados por coma. Default: `greedy,dp,backtracking` |

**Notas:**
- Backtracking se rechaza automáticamente si `amount > 60`.
- La optimalidad de Greedy se verifica internamente contra DP.
- Los resultados se devuelven siempre en el orden: greedy → dp → backtracking.

---

## 6.1 Exportar resultados y análisis

Además de la interfaz web, esta aplicación ofrece endpoints para exportar resultados y análisis.

- `GET /export_csv?coins=1,5,6&amount=10&algorithms=greedy,dp`
- `GET /export_pdf?coins=1,5,6&amount=10&algorithms=greedy,dp`
- `GET /export_analysis_csv?coins=1,5,6&max_amount=100`
- `GET /export_analysis_pdf?coins=1,5,6&max_amount=100`

En todos los casos los parámetros son:
- `coins`: denominaciones separadas por coma.
- `amount`: monto objetivo para resolver el cambio.
- `algorithms`: algoritmos separados por coma para incluir en la exportación.
- `max_amount`: monto máximo para el análisis comparativo.

> Nota: La exportación a PDF utiliza la librería `reportlab`, que está incluida en las dependencias del proyecto.

---

## 7. Tests y resultados

### Tests unitarios

El proyecto incluye tests unitarios para cada módulo de algoritmo:

```bash
uv run python -m pytest tests -q
```

```
tests/test_greedy.py              
tests/test_dynamic_programming.py 
tests/test_backtracking.py        
```

### Tests de integración con TestSprite

Se ejecutaron **15 tests automatizados de integración y UI** usando [TestSprite](https://www.testsprite.com), que verifica el comportamiento real de la aplicación corriendo en localhost.

**Resultado: 15/15 tests pasaron — 100%**

| Grupo de requisito | Tests | Resultado |
|---|---|---|
| Resolver via formulario HTML | 8 | Todos pasaron |
| Resolver via API REST | 4 | Todos pasaron |
| Análisis de rendimiento | 2 | Todos pasaron |
| Verificación de optimalidad Greedy | 1 | Pasó |
| **Total** | **15** | **15 / 0** |

**Casos cubiertos:**
- Resolver con todos los algoritmos simultáneamente.
- Resolver solo con Greedy y verificar que la optimalidad se calcula contra DP.
- Rechazar envío sin ningún algoritmo seleccionado.
- Rechazar denominaciones inválidas (no numéricas, negativas, cero).
- Endpoint REST con uno o múltiples algoritmos.
- Comparar resultados de todos los algoritmos sobre la misma entrada.
- Ejecutar análisis comparativo y verificar que se generan gráficas y tabla de resumen.

El reporte completo se encuentra en [`testsprite_tests/testsprite-mcp-test-report.md`](./testsprite_tests/testsprite-mcp-test-report.md).

---

## 8. Estructura del proyecto

```
coin-change/
├── app.py                          # Punto de entrada FastAPI, todos los endpoints
├── requirements.txt                # Dependencias del proyecto
├── README.md
│
├── src/
│   ├── coins.py                    # Sistemas de monedas predefinidos
│   ├── schemas.py                  # Modelos Pydantic v2
│   ├── greedy.py                   # Algoritmo Greedy
│   ├── dynamic_programming.py      # Algoritmo DP
│   ├── backtracking.py             # Algoritmo Backtracking con poda
│   └── analysis.py                 # Benchmarks y generación de gráficas
│
├── templates/
│   ├── base.html                   # Layout compartido
│   ├── index.html                  # Formulario principal
│   ├── result.html                 # Página de resultados
│   └── analysis.html               # Página de análisis y gráficas
│
├── static/
│   ├── css/style.css
│   └── graphs/                     # PNGs generados en tiempo de ejecución
│       ├── time_analysis.png
│       ├── coins_analysis.png
│       ├── memory_analysis.png
│       └── greedy_gap_analysis.png
│
├── tests/
│   ├── test_greedy.py
│   ├── test_dynamic_programming.py
│   └── test_backtracking.py
│
└── testsprite_tests/
    ├── testsprite-mcp-test-report.md   # Reporte de tests de integración
    └── TC001_*.py ... TC015_*.py       # Código de tests generados por TestSprite
```

---

## 9. Sistemas de monedas incluidos

| Sistema | Denominaciones | Tipo | Greedy falla en |
|---|---|---|---|
| USD | `1, 5, 10, 25, 50` | Canónico | — |
| EUR | `1, 2, 5, 10, 20, 50, 100, 200` | Canónico | — |
| COP | `50, 100, 200, 500, 1000` | Canónico | — |
| No canónico #1 | `1, 5, 6` | No canónico | monto `10` |
| No canónico #2 | `1, 3, 4` | No canónico | monto `6` |
| No canónico #3 | `1, 12, 20, 25` | No canónico | monto `40` |

Los sistemas canónicos son aquellos donde la estrategia Greedy siempre produce el resultado óptimo. Los no canónicos sirven para demostrar las limitaciones del enfoque voraz.

---

## 10. Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.10+ | Lenguaje principal |
| FastAPI | Framework web y API REST |
| Uvicorn | Servidor ASGI |
| Jinja2 | Plantillas HTML |
| Pydantic v2 | Validación de datos |
| Matplotlib | Generación de gráficas |
| tracemalloc | Medición de memoria en tiempo de ejecución |
| Pytest | Tests unitarios |
| uv | Gestión de entorno y dependencias (recomendado) |
| TestSprite | Tests de integración automatizados |

---

## 11. Solución de problemas comunes

**`command not found: uv`**
Instala uv con el comando de la sección 3.1 y reinicia la terminal.

**`command not found: uvicorn`**
Con uv siempre usa `uv run uvicorn ...`. Con pip, asegúrate de haber activado el entorno virtual.

**`ModuleNotFoundError`**
Reinstala dependencias:
```bash
uv sync --requirements requirements.txt   # con uv
pip install -r requirements.txt           # con pip
```

**PowerShell no permite activar el entorno virtual**
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
venv\Scripts\Activate.ps1
```

**Los gráficos no aparecen en la página de análisis**
Los gráficos se generan en el primer análisis ejecutado. Ve a `/analysis`, ingresa denominaciones y monto, y haz clic en **Analizar**.

**Backtracking no produce resultado para montos > 60**
Es intencional. Para montos mayores a 60 la complejidad exponencial haría el servidor no responder. Usa Programación Dinámica para montos grandes.

**El análisis tarda varios segundos**
Normal para `max_amount` alto (> 500). El análisis corre los tres algoritmos para cada monto del rango 1 a `max_amount`. Para exploración rápida usa un `max_amount` entre 100 y 200.
