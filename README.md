# LÚMINA | Álgebra Studio
**Programa educativo en Python para sistemas de ecuaciones lineales 2×2**

Proyecto académico de Ingeniería de Software · 2026.

## Ejecución rápida (Windows)
1. Extrae **todo** el contenido del ZIP, conservando las carpetas `css`, `js` y `tests`.
2. Instala Python 3.10 o superior si aún no lo tienes: https://www.python.org/downloads/
3. Haz doble clic en `INICIAR_LUMINA.bat`.
4. Se abrirá la aplicación automáticamente en tu navegador. **No cierres la consola mientras la usas.**
5. Para cerrar, presiona `Ctrl + C` en la consola.

**Alternativa con VS Code o terminal:**

```bash
python app.py
```

Si el navegador no se abre, copia la dirección `http://127.0.0.1:PUERTO/` que aparece en la terminal. El puerto se elige automáticamente.

> Importante: no abras `index.html` con doble clic; el navegador debe acceder mediante `app.py`, porque los cálculos se hacen en Python.

## Estructura

```text
LUMINA_Algebra_2x2_Proyecto/
├── index.html              # Estructura de la interfaz
├── css/
│   └── styles.css          # Diseño responsivo lavanda/rosa
├── js/
│   └── app.js              # Interacciones, gráficas y conexión HTTP
├── app.py                  # Servidor local y API /api/solve
├── solver.py               # Motor algebraico en Python
├── tests/
│   └── test_solver.py      # Pruebas automatizadas
├── INICIAR_LUMINA.bat      # Inicio en Windows
└── README.md               # Este documento
```

## Ejercicios del taller

**1. Sustitución**
- `3x − y = 7`
- `x + 2y = 4`
- Solución exacta: **x = 18/7**, **y = 5/7**.

**2. Igualación**
- `5x + 2y = 16`
- `x − y = 1`
- Solución exacta: **x = 18/7**, **y = 11/7**.

## Funcionalidades
- Sustitución, igualación, reducción y regla de Cramer.
- Solución con fracciones exactas y aproximación decimal.
- Explicación matemática paso a paso.
- Comprobación en las ecuaciones originales.
- Gráfica de las rectas y del punto de intersección.
- Reconocimiento de sistemas sin solución y con infinitas soluciones.
- Captura manual de coeficientes enteros, decimales o fracciones.
- Exportación de procedimiento como texto e impresión/guardado en PDF desde el navegador.

## Pruebas automatizadas
Desde la carpeta raíz:

```bash
python -m unittest discover -s tests -v
```

## Cómo funciona
1. El estudiante introduce seis coeficientes en `index.html`.
2. `js/app.js` envía un `POST /api/solve` con los valores y el método.
3. `app.py` recibe la solicitud y ejecuta el método `solve` de `solver.py`.
4. Python utiliza `fractions.Fraction` para evitar pérdida de precisión.
5. El servidor devuelve un JSON con resultados, pasos, comprobaciones y datos del gráfico.
6. JavaScript actualiza el resultado y dibuja las rectas en un SVG interactivo con el sistema.

**Arquitectura:** las matemáticas se resuelven en Python. HTML organiza el contenido; CSS lo diseña; JavaScript presenta la solución. Funciona localmente, sin Internet ni librerías de terceros.

## Nota de autoría
Revisa el código, practica el procedimiento algebraico y prepara una explicación propia de cada parte antes de presentarlo.
