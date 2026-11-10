#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Operaciones de álgebra lineal 2×2 y 3×3 y procedimientos detallados.

Este módulo es independiente de la interfaz: Python calcula, JavaScript presenta.
Se usa Fraction para preservar resultados exactos.
"""
from __future__ import annotations
from fractions import Fraction

PRESETS = {
    "sustitucion": {"values": [3, -1, 7, 1, 2, 4], "method": "sustitucion", "name": "Ejercicio 01 · Sustitución"},
    "igualacion": {"values": [5, 2, 16, 1, -1, 1], "method": "igualacion", "name": "Ejercicio 02 · Igualación"},
}


def number(value):
    """Acepta enteros, decimales o fracciones como 3/4 sin usar eval()."""
    if isinstance(value, bool) or not isinstance(value, (int, str, float)):
        raise ValueError("Escribe números válidos en todos los campos.")
    raw = str(value).strip().replace(",", ".").replace("−", "-")
    if not raw or len(raw) > 32:
        raise ValueError("Completa todos los campos con números razonables.")
    try:
        result = Fraction(raw)
    except (ValueError, ZeroDivisionError, OverflowError):
        raise ValueError(f"No se puede interpretar «{raw}». Usa, por ejemplo, 3, -2, 0.5 o 3/4.") from None
    if abs(result.numerator) > 10**12 or result.denominator > 10**9:
        raise ValueError("El número es demasiado grande para visualizarlo con claridad.")
    return result


def f(value: Fraction, negative_symbol="−") -> str:
    n, d = value.numerator, value.denominator
    s = str(abs(n)) if d == 1 else f"{abs(n)}/{d}"
    return (negative_symbol if n < 0 else "") + s


def dec(value: Fraction) -> str:
    return f"{float(value):.4f}".replace("-", "−")


def term(value: Fraction, variable: str, first: bool) -> str:
    if not value:
        return ""
    sign = "−" if value < 0 else ("" if first else "+")
    magnitude = abs(value)
    coef = "" if magnitude == 1 else f(magnitude)
    if first:
        return f"{sign}{coef}{variable}"
    return f" {sign} {coef}{variable}"


def linear(x: Fraction, y: Fraction, c: Fraction, vx="x", vy="y") -> str:
    result = term(x, vx, True)
    result += term(y, vy, not bool(result))
    return f"{result or '0'} = {f(c)}"


def expression(slope: Fraction, const: Fraction, variable="x") -> str:
    """slope·variable + const, con signos matemáticos legibles."""
    main = term(slope, variable, True)
    if not main:
        return f(const)
    if not const:
        return main
    return f"{main} {'+' if const > 0 else '−'} {f(abs(const))}"


def step(title: str, *lines: str, note="") -> dict:
    return {"title": title, "lines": list(lines), "note": note}


def check_lines(a, b, c, d, e, h, x, y):
    first, second = a*x+b*y, d*x+e*y
    return [
        {"equation": "Ecuación 1", "detail": f"({f(a)})({f(x)}) + ({f(b)})({f(y)}) = {f(first)}", "expected": f(c), "pass": first == c},
        {"equation": "Ecuación 2", "detail": f"({f(d)})({f(x)}) + ({f(e)})({f(y)}) = {f(second)}", "expected": f(h), "pass": second == h},
    ]


def substitution(a,b,c,d,e,h,x,y):
    # Se despeja la variable cuyo coeficiente es más sencillo.
    choices = [(abs(v) != 1, abs(v), i, var) for i, (var, v) in
               enumerate((("x",a),("y",b),("x",d),("y",e))) if v]
    _,_,choice,var = min(choices)
    first_eq = choice < 2
    A,B,C = (a,b,c) if first_eq else (d,e,h)
    D,E,F = (d,e,h) if first_eq else (a,b,c)
    eq_id = 1 if first_eq else 2
    other_id = 2 if first_eq else 1

    if var == "y":
        const, slope = C/B, -A/B
        coeff, const_other = D + E*slope, F - E*const
        result_other = x
        replaced = f"{expression(D, Fraction(0))} + ({f(E)})({expression(slope,const)}) = {f(F)}" if D else f"({f(E)})({expression(slope,const)}) = {f(F)}"
        isolate = f"y = {expression(slope,const)}"
        final = f"y = {expression(slope,const)} = {f(y)}"
        solved_var = "x"
    else:
        const, slope = C/A, -B/A
        coeff, const_other = D*slope + E, F - D*const
        result_other = y
        replaced = f"({f(D)})({expression(slope,const,'y')}) + {term(E,'y',True)} = {f(F)}" if E else f"({f(D)})({expression(slope,const,'y')}) = {f(F)}"
        isolate = f"x = {expression(slope,const,'y')}"
        final = f"x = {expression(slope,const,'y')} = {f(x)}"
        solved_var = "y"
    return [
        step("Despejar una variable", linear(A,B,C), isolate,
             note=f"Elegimos la ecuación {eq_id} porque permite despejar {var} con facilidad."),
        step("Sustituir en la otra ecuación", f"Ecuación {other_id}: {linear(D,E,F)}", replaced,
             note=f"Reemplazamos la expresión de {var} en la ecuación {other_id}."),
        step("Agrupar términos y resolver", f"{expression(coeff,Fraction(0),solved_var)} = {f(const_other)}",
             f"{solved_var} = ({f(const_other)}) / ({f(coeff)}) = {f(result_other)}",
             note="Simplificamos y obtenemos la primera incógnita."),
        step("Encontrar la variable restante", final,
             f"Solución: x = {f(x)}   ·   y = {f(y)}",
             note="Reemplazamos el valor obtenido en el despeje inicial."),
    ]


def equalization(a,b,c,d,e,h,x,y):
    possibilities = []
    if a and d:
        possibilities.append((abs(a)+abs(d), "x"))
    if b and e:
        possibilities.append((abs(b)+abs(e), "y"))
    if not possibilities:
        # Sistemas separados como 2x=4, 3y=9: la igualación no aplica
        # directamente a una misma incógnita en las dos ecuaciones.
        return [
            step("Identificar el caso especial", linear(a,b,c),linear(d,e,h),
                 note="No hay una variable con coeficiente distinto de cero en ambas ecuaciones."),
            step("Resolver cada condición",f"x = {f(x)}",f"y = {f(y)}",
                 note="Cada ecuación determina por separado una incógnita; no es necesario igualar expresiones."),
        ]
    _,var = min(possibilities)
    if var == "y":
        slope1, const1 = -a/b, c/b
        slope2, const2 = -d/e, h/e
        other = "x"
        result_other, result_var = x,y
    else:
        slope1, const1 = -b/a, c/a
        slope2, const2 = -e/d, h/d
        other = "y"
        result_other, result_var = y,x
    difference = slope1 - slope2
    right = const2 - const1
    return [
        step(f"Despejar {var} en ambas ecuaciones",
             f"Ecuación 1 → {var} = {expression(slope1,const1,other)}",
             f"Ecuación 2 → {var} = {expression(slope2,const2,other)}",
             note="Las dos expresiones representan la misma incógnita."),
        step("Igualar las expresiones",
             f"{expression(slope1,const1,other)} = {expression(slope2,const2,other)}",
             note=f"Como ambas equivalen a {var}, pueden igualarse."),
        step("Reunir términos semejantes",
             f"{expression(difference,Fraction(0),other)} = {f(right)}",
             f"{other} = ({f(right)}) / ({f(difference)}) = {f(result_other)}",
             note=f"Resolvemos la ecuación con una incógnita y obtenemos {other}."),
        step(f"Calcular {var}",
             f"{var} = {expression(slope1,const1,other)} = {f(result_var)}",
             f"Solución: x = {f(x)}   ·   y = {f(y)}",
             note="Sustituimos en uno de los despejes iniciales."),
    ]


def elimination(a,b,c,d,e,h,x,y):
    # Evita confundir signos mostrando las multiplicaciones explícitas.
    if b and e:
        m1, m2 = e,-b
        K, R, var = a*e-b*d, c*e-b*h, "x"
        other_var, other_result = "y", y
    elif a and d:
        m1, m2 = d,-a
        K, R, var = b*d-a*e, c*d-a*h, "y"
        other_var, other_result = "x",x
    else:
        return [step("Resolver las ecuaciones independientes",f"x = {f(x)}", f"y = {f(y)}",
                     note="Cada ecuación contiene una variable distinta.")]
    return [
        step("Elegir la variable que se elimina", linear(a,b,c),linear(d,e,h),
             note=f"Multiplicamos la primera ecuación por {f(m1)} y la segunda por {f(m2)} para cancelar {other_var}."),
        step("Multiplicar y sumar", linear(a*m1,b*m1,c*m1), linear(d*m2,e*m2,h*m2),
             f"{expression(K,Fraction(0),var)} = {f(R)}",
             note=f"Al sumar ambas ecuaciones desaparece {other_var}."),
        step("Encontrar ambas incógnitas", f"{var} = ({f(R)}) / ({f(K)}) = {f(x if var == 'x' else y)}",
             f"{other_var} = {f(other_result)}",
             f"Solución: x = {f(x)}   ·   y = {f(y)}",
             note="Sustituimos el primer valor en cualquiera de las ecuaciones originales."),
    ]


def cramer(a,b,c,d,e,h,x,y):
    det = a*e-b*d
    dx = c*e-b*h
    dy = a*h-c*d
    return [
        step("Determinante de la matriz de coeficientes",
             f"D = ({f(a)})({f(e)}) − ({f(b)})({f(d)}) = {f(det)}",
             note="Como D es distinto de cero, hay una solución única."),
        step("Determinantes auxiliares",
             f"Dₓ = ({f(c)})({f(e)}) − ({f(b)})({f(h)}) = {f(dx)}",
             f"Dᵧ = ({f(a)})({f(h)}) − ({f(c)})({f(d)}) = {f(dy)}",
             note="Se reemplaza la columna de cada variable por los resultados."),
        step("Aplicar la regla de Cramer",
             f"x = Dₓ/D = {f(dx)}/{f(det)} = {f(x)}",
             f"y = Dᵧ/D = {f(dy)}/{f(det)} = {f(y)}",
             note="Ambos valores satisfacen las dos ecuaciones originales."),
    ]


def solve(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Los datos de la solicitud no son válidos.")
    operation = payload.get("operation", "system")
    if operation not in ("system", "determinant"):
        raise ValueError("Selecciona una operación válida.")
    if operation == "determinant":
        return solve_sarrus(payload)
    dimension = payload.get("dimension", 2)
    if type(dimension) is not int or dimension not in (2, 3):
        raise ValueError("La dimensión debe ser 2 o 3.")
    if dimension == 3:
        return solve3(payload)
    values = payload.get("values")
    method = payload.get("method", "sustitucion")
    if not isinstance(values, list) or len(values) != 6:
        raise ValueError("El sistema debe contener seis coeficientes.")
    if not isinstance(method, str) or method not in {"sustitucion", "igualacion", "reduccion", "cramer"}:
        raise ValueError("Selecciona un método válido.")
    a,b,c,d,e,h = [number(v) for v in values]
    D = a*e-b*d
    dx = c*e-b*h
    dy = a*h-c*d
    common = {
        "equations": [linear(a,b,c),linear(d,e,h)],
        "coefficients": [float(v) for v in (a,b,c,d,e,h)],
        "method": method,
        "methodLabel": {"sustitucion":"Sustitución", "igualacion":"Igualación", "reduccion":"Reducción", "cramer":"Regla de Cramer"}[method],
    }
    if not D:
        infinite = (dx == 0 and dy == 0 and
                    not ((a == 0 and b == 0 and c != 0) or
                         (d == 0 and e == 0 and h != 0)))
        status = "infinite" if infinite else "none"
        comment = "Las dos ecuaciones representan la misma recta (o identidades). Hay infinitas soluciones." if infinite else "Las rectas son paralelas e incompatibles. No existe un punto de intersección."
        return {**common, "ok": True, "status": status, "result": None,
                "headline": "Infinitas soluciones" if infinite else "Sin solución",
                "explanation": comment,
                "steps": [step("Revisar el determinante",f"D = ({f(a)})({f(e)}) − ({f(b)})({f(d)}) = 0",
                               note="El determinante cero impide obtener una solución única."),
                          step("Comparar las ecuaciones", f"Dₓ = {f(dx)}   ·   Dᵧ = {f(dy)}",
                               comment, note="La clasificación se hace comparando las ecuaciones completas.")],
                "checks": []}
    x, y = dx/D, dy/D
    functions = {"sustitucion":substitution,"igualacion":equalization,"reduccion":elimination,"cramer":cramer}
    details = functions[method](a,b,c,d,e,h,x,y)
    return {**common, "ok":True, "status":"unique", "headline":"Solución única encontrada",
            "explanation":"Las dos rectas se cruzan en un único punto.",
            "result":{"x":f(x),"y":f(y),"xDecimal":dec(x),"yDecimal":dec(y),"xNumber":float(x),"yNumber":float(y)},
            "steps":details,"checks":check_lines(a,b,c,d,e,h,x,y)}




def determinant3(matrix):
    """Expansión por la primera fila: +, −, +; siempre exacta."""
    a, b, c = matrix[0]
    d, e, g = matrix[1]
    h, i, j = matrix[2]
    return a*(e*j-g*i) - b*(d*j-g*h) + c*(d*i-e*h)


def matrix_lines(matrix):
    return ["[ " + "   ".join(f(v) for v in row) + " ]" for row in matrix]


def determinant_detail(matrix):
    a, b, c = matrix[0]
    d, e, g = matrix[1]
    h, i, j = matrix[2]
    return (f"({f(a)})[({f(e)})({f(j)}) − ({f(g)})({f(i)})]"
            f" − ({f(b)})[({f(d)})({f(j)}) − ({f(g)})({f(h)})]"
            f" + ({f(c)})[({f(d)})({f(i)}) − ({f(e)})({f(h)})]")


def exact_ranks(augmented):
    """Gauss-Jordan en las tres columnas de A, con registro de operaciones."""
    rows = [row[:] for row in augmented]
    pivot = 0
    operations = []
    for col in range(3):
        selected = next((r for r in range(pivot, 3) if rows[r][col]), None)
        if selected is None:
            continue
        if selected != pivot:
            rows[pivot], rows[selected] = rows[selected], rows[pivot]
            operations.append(f"F{pivot+1} ↔ F{selected+1}")
        scale = rows[pivot][col]
        rows[pivot] = [v/scale for v in rows[pivot]]
        operations.append(f"F{pivot+1} ← F{pivot+1} / ({f(scale)})")
        for r in range(3):
            if r != pivot and rows[r][col]:
                scale = rows[r][col]
                rows[r] = [v-scale*w for v, w in zip(rows[r], rows[pivot])]
                operations.append(f"F{r+1} ← F{r+1} − ({f(scale)})F{pivot+1}")
        pivot += 1
    contradiction = any(not any(row[:3]) and row[3] for row in rows)
    return pivot, pivot + int(contradiction), rows, operations


def solve3(payload):
    method = payload.get("method", "cramer3")
    if method != "cramer3":
        raise ValueError("Para 3×3 selecciona Determinantes 3×3 (regla de Cramer).")
    values = payload.get("values")
    if not isinstance(values, list) or len(values) != 12:
        raise ValueError("El sistema 3×3 debe contener doce coeficientes.")
    values = [number(v) for v in values]
    rows = [values[i:i+4] for i in range(0, 12, 4)]
    matrix = [row[:3] for row in rows]
    rhs = [row[3] for row in rows]
    equations = []
    for row in rows:
        expression3 = ""
        for coef, variable in zip(row[:3], "xyz"):
            expression3 += term(coef, variable, not bool(expression3))
        equations.append(f"{expression3 or '0'} = {f(row[3])}")
    determinants = {}
    details = [step("Escribir A · (x, y, z)ᵀ = b", *equations,
                    "Matriz A:", *matrix_lines(matrix), "Vector b: " + str([f(v) for v in rhs]))]
    for column, name in [(-1, "D"), (0, "Dx"), (1, "Dy"), (2, "Dz")]:
        current = [row[:] for row in matrix]
        if column >= 0:
            for r in range(3):
                current[r][column] = rhs[r]
        value = determinant3(current)
        determinants[name] = {"value": f(value), "matrix": [[f(v) for v in row] for row in current]}
        details.append(step(f"Calcular {name}", *matrix_lines(current),
                            name + " = " + determinant_detail(current) + " = " + f(value),
                            note="Expansión por la primera fila con signos +, −, +." if column < 0 else
                            f"Reemplazamos la columna de {'xyz'[column]} por el vector b y expandimos con signos +, −, +."))
    common = {"ok": True, "dimension": 3, "method": method,
              "methodLabel": "Determinantes 3×3 (regla de Cramer)",
              "equations": equations, "determinants": determinants, "steps": details}
    D = determinant3(matrix)
    if not D:
        rank_a, rank_aug, reduced, operations = exact_ranks(rows)
        infinite = rank_a == rank_aug
        explanation = ("Los rangos son iguales y menores que 3: hay infinitas soluciones."
                       if infinite else "El rango de A es menor que el de [A|b]: el sistema es incompatible.")
        details.append(step("Clasificar mediante eliminación exacta", *operations,
                            "Matriz reducida [A|b]:", *matrix_lines(reduced),
                            f"rango(A) = {rank_a}; rango([A|b]) = {rank_aug}", explanation,
                            note="D = 0: no podemos dividir por D; los rangos deciden la compatibilidad."))
        return {**common, "status": "infinite" if infinite else "none", "result": None,
                "headline": "Infinitas soluciones" if infinite else "Sin solución",
                "explanation": explanation, "ranks": {"A": rank_a, "augmented": rank_aug}, "checks": []}
    solution = []
    for col in range(3):
        replaced = [[rhs[r] if c == col else matrix[r][c] for c in range(3)] for r in range(3)]
        solution.append(determinant3(replaced)/D)
    result = {}
    lines = []
    for variable, value, name in zip("xyz", solution, ("Dx", "Dy", "Dz")):
        result.update({variable: f(value), variable+"Decimal": dec(value)})
        lines.append(f"{variable} = {name}/D = ({determinants[name]['value']}) / ({f(D)}) = {f(value)} ≈ {dec(value)}")
    details.append(step("Aplicar la regla de Cramer", *lines, note="D ≠ 0: existe una solución única."))
    checks = []
    for i, row in enumerate(rows):
        actual = sum((a*b for a, b in zip(row[:3], solution)), Fraction(0))
        substitution = " + ".join(f"({f(a)})({f(b)})" for a, b in zip(row[:3], solution))
        checks.append({"equation": f"Ecuación {i+1}", "detail": f"{substitution} = {f(actual)} = {f(row[3])}",
                       "expected": f(row[3]), "pass": actual == row[3]})
    return {**common, "status": "unique", "headline": "Solución única encontrada",
            "explanation": "Los valores satisfacen simultáneamente las tres ecuaciones.",
            "result": result, "checks": checks}


# Los seis productos conservan sus signos antes de restar los ascendentes.
def solve_sarrus(payload):
    dimension = payload.get("dimension", 3)
    if type(dimension) is not int or dimension != 3:
        raise ValueError("Sarrus requiere una matriz de dimensión 3.")
    if payload.get("method", "sarrus") != "sarrus":
        raise ValueError("Selecciona el método Sarrus para el determinante.")
    values = payload.get("values")
    if not isinstance(values, list) or len(values) != 9:
        raise ValueError("La matriz 3×3 debe contener nueve entradas, por filas.")
    values = [number(v) for v in values]
    matrix = [values[i:i+3] for i in range(0,9,3)]
    extended = [row + row[:2] for row in matrix]
    paths = [([0,c],[1,c+1],[2,c+2]) for c in range(3)]
    paths += [([2,c],[1,c+1],[0,c+2]) for c in range(3)]
    products = []
    exact_products = []
    for i, path in enumerate(paths):
        factors = [extended[r][c] for r,c in path]
        value = factors[0]*factors[1]*factors[2]
        exact_products.append(value)
        name = ("P" if i < 3 else "Q") + str(i%3+1)
        formula = " · ".join("("+f(v)+")" for v in factors)
        products.append({"name":name,"direction":"down" if i<3 else "up",
                         "path":path,"value":f(value),"formula":formula})
    down = sum(exact_products[:3], Fraction(0))
    up = sum(exact_products[3:], Fraction(0))
    result = down-up
    reference = determinant3(matrix)
    details = [
        step("Escribir la matriz original", *matrix_lines(matrix), note="Leemos las nueve entradas por filas."),
        step("Repetir las dos primeras columnas a la derecha", *matrix_lines(extended),
             note="La matriz auxiliar tiene tres filas y cinco columnas; solo sirve para seguir las diagonales."),
        step("Multiplicar las diagonales descendentes ↘", *[item["name"]+" = "+item["formula"]+" = "+item["value"] for item in products[:3]],
             "S↘ = " + " + ".join("("+item["value"]+")" for item in products[:3]) + " = " + f(down)),
        step("Multiplicar las diagonales ascendentes ↗", *[item["name"]+" = "+item["formula"]+" = "+item["value"] for item in products[3:]],
             "S↗ = " + " + ".join("("+item["value"]+")" for item in products[3:]) + " = " + f(up)),
        step("Restar las sumas: det(A) = S↘ − S↗", f"det(A) = ({f(down)}) − ({f(up)}) = {f(result)}",
             f"det(A) ≈ {dec(result)}", note="Restamos la suma ascendente completa, conservando los signos de los productos."),
        step("Comprobar por expansión de la primera fila", "det(A) = "+determinant_detail(matrix)+" = "+f(reference),
             note="La expansión independiente confirma el resultado de Sarrus.")]
    return {"ok":True,"operation":"determinant","dimension":3,"method":"sarrus",
            "methodLabel":"Regla de Sarrus", "status":"determinant", "headline":"Determinante calculado",
            "explanation":"det(A) = suma descendente − suma ascendente. " +
                ("El determinante es cero: la matriz es singular." if not result else "El determinante es distinto de cero: la matriz es invertible."),
            "equations":matrix_lines(matrix), "matrix":[[f(v) for v in row] for row in matrix],
            "extendedMatrix":[[f(v) for v in row] for row in extended], "products":products,
            "sums":{"down":f(down),"up":f(up)},"result":{"determinant":f(result),"decimal":dec(result)},
            "steps":details,"checks":[{"equation":"Expansión por cofactores", "detail":"det(A) = "+f(reference),
            "expected":f(result),"pass":reference==result}]}
