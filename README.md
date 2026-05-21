# Coin Change — Problema del Cambio de Moneda

Tres enfoques algorítmicos para resolver el problema clásico del cambio de moneda, con interfaz web interactiva y análisis comparativo de rendimiento.

## Descripción del problema

Dado un conjunto de denominaciones de monedas y un monto objetivo, encontrar la **mínima cantidad de monedas** necesarias para formar ese monto exacto.

### Ejemplo

```
Monedas:  [1, 5, 6]
Monto:    11

Solución voraz:    5 + 5 + 1  = 3 monedas  (no óptima)
Solución óptima:   6 + 5      = 2 monedas
```

## Paradigmas implementados

| Algoritmo | Archivo | Complejidad | ¿Siempre óptimo? |
|---|---|---|---|
| **Voraz (Greedy)** | `src/greedy.py` | O(n) | No |
| **Programación Dinámica** | `src/dynamic_programming.py` | O(m × n) | Sí |
| **Backtracking** | `src/backtracking.py` | O(2ⁿ) exponencial | Sí |

### 1. Algoritmo Voraz (Greedy)

Selecciona siempre la moneda de mayor denominación que no supere el monto restante.

- **Ventaja:** Extremadamente rápido (O(n)).
- **Desventaja:** No garantiza la solución óptima para sistemas de monedas no canónicos.

### 2. Programación Dinámica (Bottom-Up)

Construye una tabla `dp[]` donde `dp[i]` almacena la mínima cantidad de monedas para el monto `i`. Luego reconstruye la solución recorriendo la tabla hacia atrás.

- **Ventaja:** Siempre encuentra la solución óptima con complejidad polinomial O(m × n).
- **Desventaja:** Requiere memoria adicional O(m) para la tabla.

### 3. Backtracking con poda

Explora recursivamente todas las combinaciones posibles, podando ramas que superan la mejor solución conocida.

- **Ventaja:** Siempre encuentra la solución óptima.
- **Desventaja:** Complejidad exponencial; solo práctico para montos pequeños (≤ 60).

## Estructura del proyecto

```
coin-change/
├── README.md                          # Documentación del proyecto
├── requirements.txt                   # Dependencias del proyecto
├── .gitignore                         # Archivos ignorados por git
│
├── app.py                             # Servidor FastAPI (punto de entrada)
│
├── src/                               # Lógica de los algoritmos
│   ├── __init__.py
│   ├── coins.py                       # Sistemas monetarios predefinidos
│   ├── schemas.py                     # Modelos Pydantic (request/response)
│   ├── greedy.py                      # Algoritmo Voraz
│   ├── dynamic_programming.py         # Programación Dinámica
│   ├── backtracking.py                # Backtracking / Fuerza Bruta
│   └── analysis.py                    # Benchmarking y generación de gráficos
│
├── static/
│   ├── css/
│   │   └── style.css                  # Estilos de la interfaz web
│   └── graphs/                        # Gráficos generados (PNG)
│
├── templates/                         # Plantillas HTML (Jinja2)
│   ├── base.html                      # Plantilla base (navbar, footer)
│   ├── index.html                     # Formulario principal
│   ├── result.html                    # Resultados con visualización
│   └── analysis.html                  # Análisis comparativo con gráficos
│
└── tests/                             # Tests unitarios
    ├── __init__.py
    ├── test_greedy.py
    ├── test_dynamic_programming.py
    └── test_backtracking.py
```

## Requisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd coin-change
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\activate

# Windows (CMD)
venv\Scripts\activate.bat
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
uvicorn app:app --reload
```

O también:

```bash
python app.py
```

### 5. Abrir en el navegador

```
http://localhost:8000
```

## Uso

### Interfaz web

1. **Inicio (`/`):** Selecciona un sistema de monedas predefinido o ingresa denominaciones personalizadas, define el monto objetivo y elige qué algoritmos ejecutar.
2. **Resultados:** Muestra las monedas utilizadas, cantidad, tiempo de ejecución y permite expandir detalles como la tabla de DP y los pasos del greedy.
3. **Análisis (`/analysis`):** Ejecuta benchmarks con montos crecientes y genera gráficos comparativos de tiempo de ejecución y cantidad de monedas usadas.

### API REST

```bash
# Ejemplo: resolver con monedas [1,5,6] para monto 11
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
      "optimal": true,
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

## Ejecutar tests

```bash
# Todos los tests
python -m pytest tests/ -v

# Test específico
python -m pytest tests/test_greedy.py -v
```

### Verificar estilo PEP8

```bash
pip install flake8
flake8 src/ tests/ app.py
```

## Análisis comparativo esperado

| Aspecto | Voraz (Greedy) | Programación Dinámica | Backtracking |
|---|---|---|---|
| **Tiempo de ejecución** | Más rápido (O(n)) | Rápido (O(m·n)) | Muy lento (O(2ⁿ)) |
| **Uso de memoria** | Mínimo (O(1)) | Moderado (O(m)) | Alto (pila de recursión) |
| **Solución óptima** | No siempre | Siempre | Siempre |
| **Recomendado para** | Sistemas canónicos, tiempo crítico | Uso general | Montos pequeños, fines educativos |

## Tecnologías utilizadas

- **Python 3.10+** — Lenguaje de programación
- **FastAPI** — Framework web para la API
- **Jinja2** — Motor de plantillas HTML
- **Matplotlib** — Generación de gráficos comparativos
- **Pydantic** — Validación de datos con modelos
- **Pytest** — Framework de tests unitarios
- **Flake8** — Linter para garantizar PEP8

## Licencia

Proyecto académico para la asignatura de **Algoritmo y Complejidad**.

### Integrantes

- Shalom Jhoanna Arrieta Marrugo
- Alejandro Patron Montero
- Dariem Garcia Cardona
- Dayana Narvaez
- Lineth Villalba
