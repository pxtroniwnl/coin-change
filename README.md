# Coin Change - Problema del Cambio de Moneda

Aplicación web interactiva hecha con **FastAPI** para resolver el problema clásico del cambio de moneda usando tres paradigmas algorítmicos:

- **Greedy / Voraz**
- **Programación Dinámica**
- **Backtracking con poda**

La aplicación permite resolver un caso puntual, visualizar los resultados y generar un análisis comparativo usando la misma configuración ingresada por el usuario.

> Proyecto Final - Algoritmo y Complejidad - 2026
> Shalom Jhoanna Arrieta Marrugo - Alejandro Patron Montero - Dariem Garcia Cardona - Dayana Narvaez - Lineth Villalba

---

## Descripción del problema

Dado un conjunto de denominaciones de monedas y un monto objetivo, se busca formar ese monto usando la **menor cantidad posible de monedas**.

Ejemplo donde Greedy falla:

```text
Monedas: [1, 5, 6]
Monto:   10

Solución Greedy: 6 + 1 + 1 + 1 + 1 = 5 monedas
Solución óptima: 5 + 5             = 2 monedas
```

Este caso es útil porque muestra que elegir siempre la moneda más grande posible puede ser rápido, pero no siempre produce la solución óptima.

---

## Requisitos previos

- **Python 3.10 o superior**
- **pip**
- **git**

Verifica tu versión de Python:

```bash
python --version
```

En algunos sistemas puede ser necesario usar:

```bash
python3 --version
```

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd coin-change
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv

# Linux / macOS
python3 -m venv venv
```

### 3. Activar entorno virtual

```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux / macOS
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala FastAPI, Uvicorn, Jinja2, Matplotlib, python-multipart, Pydantic y Pytest.

---

## Ejecutar la aplicación

Con el entorno virtual activado:

```bash
uvicorn app:app --reload
```

También puedes ejecutarla directamente:

```bash
python app.py
```

Luego abre:

```text
http://localhost:8000
```

Para detener el servidor, presiona `Ctrl + C`.

---

## Flujo principal de uso

1. Abre la página de inicio (`/`).
2. Ingresa las denominaciones, por ejemplo `1,5,6`.
3. Ingresa el monto objetivo, por ejemplo `25`.
4. Selecciona los algoritmos que quieres ejecutar.
5. Haz clic en **Resolver**.
6. Revisa los resultados por algoritmo.
7. Haz clic en **Ver análisis**.
8. La página de análisis se genera automáticamente usando las mismas monedas y el mismo monto ingresado en Resolver.

El enlace de análisis queda con parámetros en la URL, por ejemplo:

```text
/analysis?coins=1%2C5%2C6&max_amount=25
```

Esto evita que el usuario tenga que escribir nuevamente las denominaciones y mantiene continuidad entre resultados y análisis.

---

## Página principal - Resolver (`/`)

La página principal permite:

- Seleccionar un sistema de monedas predefinido.
- Escribir denominaciones personalizadas separadas por coma.
- Ingresar un monto objetivo.
- Seleccionar Greedy, Programación Dinámica y/o Backtracking.
- Ver monedas usadas, cantidad total, tiempo de ejecución y detalles del algoritmo.

Backtracking está limitado a montos `<= 60` en la interfaz para evitar tiempos de espera excesivos.

---

## Página de análisis (`/analysis`)

La página de análisis ahora puede funcionar de dos formas:

1. **Desde resultados:** recibe automáticamente `coins` y `max_amount` desde el botón **Ver análisis**.
2. **Directamente:** si se abre `/analysis` sin parámetros, muestra un formulario para configurar el análisis manualmente.

El análisis genera:

- Gráfica de **tiempo de ejecución vs monto**.
- Gráfica de **memoria pico vs monto** medida con `tracemalloc`.
- Gráfica de **cantidad de monedas usadas vs monto**.
- Gráfica de **brecha Greedy vs Programación Dinámica**.
- Tabla de complejidad algorítmica.
- Resumen comparativo con:
  - algoritmo más rápido,
  - algoritmo con menor memoria promedio,
  - algoritmo recomendado para uso general,
  - algoritmo menos adecuado para montos grandes.
- Tabla de promedios de tiempo y memoria.
- Tabla completa de datos del análisis.

Backtracking se evalúa solo hasta `60` aunque el análisis tenga un monto máximo mayor, porque su costo crece de forma exponencial.

---

## API REST (`/api/solve`)

También puedes resolver casos desde HTTP:

```bash
curl "http://localhost:8000/api/solve?coins=1,5,6&amount=10&algorithms=greedy,dp"
```

Respuesta esperada:

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

Parámetros:

| Parámetro | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `coins` | string | Denominaciones separadas por coma | `1,5,10,25` |
| `amount` | entero | Monto objetivo | `47` |
| `algorithms` | string | Algoritmos separados por coma | `greedy,dp` |

Notas:

- Las denominaciones deben ser enteros positivos.
- El monto debe ser no negativo.
- Backtracking también se limita para montos mayores a `60` en la API.
- La optimalidad de Greedy se verifica comparando contra Programación Dinámica.

---

## Ejecutar tests

```bash
python -m pytest tests -q
```

También puedes ejecutar archivos individuales:

```bash
python -m pytest tests/test_greedy.py -v
python -m pytest tests/test_dynamic_programming.py -v
python -m pytest tests/test_backtracking.py -v
```

---

## Algoritmos implementados

### 1. Greedy / Voraz - `src/greedy.py`

Ordena las monedas de mayor a menor y toma siempre la moneda más grande que no supere el monto restante.

```text
Complejidad temporal: O(n)
Complejidad espacial: O(1)
Óptimo garantizado:   No
```

Es muy rápido, pero puede fallar en sistemas no canónicos.

Ejemplos:

- `[1, 5, 6]`, monto `10`: Greedy usa 5 monedas; óptimo usa 2.
- `[1, 3, 4]`, monto `6`: Greedy usa 3 monedas; óptimo usa 2.
- `[1, 12, 20, 25]`, monto `40`: Greedy usa 5 monedas; óptimo usa 2.

### 2. Programación Dinámica - `src/dynamic_programming.py`

Construye una tabla `dp[]` donde `dp[i]` representa la mínima cantidad de monedas necesarias para formar el monto `i`.

```text
Complejidad temporal: O(m x n)
Complejidad espacial: O(m)
Óptimo garantizado:   Sí
```

Es la opción más recomendable para uso general porque garantiza la solución óptima con costo polinomial.

### 3. Backtracking con poda - `src/backtracking.py`

Explora combinaciones posibles de monedas de forma recursiva y descarta ramas que ya no pueden mejorar la mejor solución encontrada.

```text
Complejidad temporal: Exponencial
Complejidad espacial: O(profundidad)
Óptimo garantizado:   Sí
Límite práctico:      Montos <= 60
```

Es útil para fines educativos, pero no es adecuado para montos grandes.

---

## Comparación general

| Aspecto | Greedy | Programación Dinámica | Backtracking |
|---|---|---|---|
| Paradigma | Voraz | Bottom-up | Búsqueda exhaustiva con poda |
| Tiempo | O(n) | O(m x n) | Exponencial |
| Memoria | O(1) | O(m) | O(profundidad) |
| Garantiza óptimo | No | Sí | Sí |
| Escala bien | Sí | Sí | No |
| Uso recomendado | Sistemas canónicos o tiempo crítico | Uso general | Explicación académica |

Conclusión: Greedy suele ser el más rápido y consume poca memoria, pero no garantiza optimalidad. Programación Dinámica es la mejor opción general. Backtracking encuentra el óptimo, pero su costo lo vuelve inviable para montos grandes.

---

## Estructura del proyecto

```text
coin-change/
├── app.py
├── requirements.txt
├── README.md
│
├── src/
│   ├── coins.py
│   ├── schemas.py
│   ├── greedy.py
│   ├── dynamic_programming.py
│   ├── backtracking.py
│   └── analysis.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── analysis.html
│
├── static/
│   ├── css/style.css
│   └── graphs/
│       ├── time_analysis.png
│       ├── coins_analysis.png
│       ├── memory_analysis.png
│       └── greedy_gap_analysis.png
│
└── tests/
    ├── test_greedy.py
    ├── test_dynamic_programming.py
    └── test_backtracking.py
```

---

## Sistemas de monedas incluidos

| Sistema | Denominaciones | Tipo | Greedy falla en |
|---|---|---|---|
| USD | `1, 5, 10, 25, 50` | Canónico | - |
| EUR | `1, 2, 5, 10, 20, 50, 100, 200` | Canónico | - |
| COP | `50, 100, 200, 500, 1000` | Canónico | - |
| No canónico #1 | `1, 5, 6` | No canónico | monto `10` |
| No canónico #2 | `1, 3, 4` | No canónico | monto `6` |
| No canónico #3 | `1, 12, 20, 25` | No canónico | monto `40` |

---

## Solución de problemas comunes

**`command not found: uvicorn`**  
Activa el entorno virtual y vuelve a ejecutar el comando.

**`ModuleNotFoundError`**  
Instala dependencias con:

```bash
pip install -r requirements.txt
```

**PowerShell no permite activar el entorno virtual**
Ejecuta:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Luego activa:

```powershell
venv\Scripts\Activate.ps1
```

**Los gráficos no aparecen**
Ejecuta un análisis desde `/analysis`. Los gráficos se generan en `static/graphs/`.

**Backtracking tarda demasiado**
Usa Programación Dinámica para montos grandes. Backtracking está limitado a `60` por seguridad.

---

## Tecnologías

- Python 3.10+
- FastAPI
- Uvicorn
- Jinja2
- Pydantic v2
- Matplotlib
- tracemalloc
- Pytest
