# LÚMINA | Álgebra Studio
**Programa educativo en Python para sistemas de ecuaciones lineales 2×2 y 3×3**

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


## Sistemas 3×3 · Determinantes (regla de Cramer)
Selecciona **Sistema 3×3**. Cada fila contiene los cuatro valores de `ax + by + cz = d`;
se aceptan enteros, negativos, decimales (punto o coma) y fracciones como `-3/4`.
El botón del ejemplo carga:

```text
 2x + y −  z =   8
−3x − y + 2z = −11
−2x + y + 2z =  −3
```

Resultado: **x=2, y=3, z=−1**, con **D=−1, Dx=−2, Dy=−3, Dz=1**.
Las tarjetas muestran las cuatro matrices, el procedimiento desarrolla cada determinante
por expansión de la primera fila (`+, −, +`) y comprueba las tres igualdades por sustitución.
Los resultados incluyen la fracción exacta y una aproximación con cuatro decimales.
Cuando D=0, la eliminación Gauss-Jordan exacta muestra operaciones, matriz reducida y rangos:
`rango(A) < rango([A|b])` significa incompatibilidad; rangos iguales menores que 3 indican infinitas soluciones.
En estos casos no se calcula un cociente ni una terna única.

En 3×3, las matrices reemplazan la gráfica 2D. La descarga de texto y la impresión/guardado
como PDF incluyen la dimensión, las ecuaciones, el desarrollo y las comprobaciones.
Al volver a 2×2 siguen disponibles los cuatro métodos, los dos ejercicios originales y la gráfica SVG.
Los campos de cada dimensión se conservan al cambiar de modo.

### API compatible
El contrato 2×2 sigue aceptando `{"method":"cramer","values":[2,3,13,4,-1,5]}`;
`dimension` es opcional y vale `2` por defecto.
Para 3×3 envía `POST /api/solve`:

```json
{"dimension":3,"method":"cramer3","values":[2,1,-1,8,-3,-1,2,-11,-2,1,2,-3]}
```

Los doce valores se agrupan por filas `[a,b,c,d]`. El único método 3×3 es `cramer3`
(también es el predeterminado al especificar dimensión 3).
La respuesta añade `dimension`, `determinants` (valores exactos y matrices), `z` y `zDecimal`
en `result`, y `ranks` para sistemas singulares. Los errores de validación devuelven HTTP 400.
El motor usa exclusivamente `fractions.Fraction`, sin dependencias externas.
Para mantener legibilidad, cada entrada tiene hasta 32 caracteres, numerador absoluto hasta
10¹² y denominador hasta 10⁹. La interfaz valida campos y denominadores; Python aplica
la validación definitiva y los límites. No se representa una gráfica 3D ni se parametrizan
las infinitas soluciones; sí se explica y demuestra su clasificación exacta.

Las pruebas cubren los cuatro métodos 2×2, archivos estáticos y API; además del ejemplo 3×3,
fracciones, decimales, negativos, rangos 0/1/2/3, determinante cero y solicitudes inválidas.


## Taller de matrices 3×3 · Regla de Sarrus
1. Abre **Determinantes · Sarrus**, junto a los dos modos de sistemas.
2. Pulsa un ejercicio **a)–h)** para cargar y resolver la matriz de la guía, o introduce
   tus nueve entradas por filas y pulsa **Calcular determinante**. No se necesitan términos independientes.
3. Revisa la matriz de tres filas y cinco columnas: se repiten las primeras dos columnas.
4. Pulsa cualquiera de los seis productos para resaltar sus factores. Las diagonales ↘
   se suman; luego se resta la suma completa de las diagonales ↗, conservando los signos.
5. El procedimiento incluye los seis productos, sus sumas, la resta final, el resultado
   exacto y decimal, y una comprobación independiente por expansión de cofactores.
6. **Descargar procedimiento** guarda el texto del ejercicio; **Guardar PDF** abre la impresión del navegador.

Resultados de la guía:

| Ejercicio | det(A) |
|---|---:|
| a | 0 |
| b | −25 |
| c | −12 |
| d | 7 |
| e | 7 |
| f | 14 |
| g | 0 |
| h | 0 |

Un determinante cero es un resultado válido de la matriz y se muestra como tal.
Este modo calcula determinantes; la clasificación de sistemas e incógnitas corresponde
al modo **Sistema 3×3**, que mantiene Cramer y su análisis por rangos.
Los modos anteriores y sus campos se conservan al cambiar de pestaña.

La API `/api/solve` incorpora una operación opcional (por defecto `system`):

```json
{"operation":"determinant","dimension":3,"method":"sarrus","values":[3,2,1,5,-2,-3,-2,4,4]}
```

La respuesta incluye `result.determinant`, `result.decimal`, `matrix`, `extendedMatrix`,
`products` (factores, recorrido y producto de cada diagonal), `sums`, `steps` y `checks`.
Solo se admiten nueve entradas, dimensión 3 y método `sarrus`; se aplican las validaciones
numéricas existentes y cálculo exacto con `Fraction`. No se agregan dependencias.
Las pruebas incluyen las ocho matrices, signos, fracciones, entradas inválidas, API y
comparación con la definición del determinante mediante permutaciones en 60 matrices adicionales.
