#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Operaciones de álgebra lineal 2×2 y procedimientos detallados.

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
        raise ValueError("Escribe números válidos en los seis campos.")
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
    values = payload.get("values")
    method = payload.get("method", "sustitucion")
    if not isinstance(values, list) or len(values) != 6:
        raise ValueError("El sistema debe contener seis coeficientes.")
    if method not in {"sustitucion", "igualacion", "reduccion", "cramer"}:
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


