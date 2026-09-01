"""
Funciones de formato numérico para el dashboard.
Formato chileno/español: punto para miles, coma para decimales.
"""


def fmt_integer(value) -> str:
    """Formatea un entero con separador de miles (punto).

    Ejemplo: 125000 → '125.000'
    """
    try:
        return f"{int(round(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "—"


def fmt_decimal(value, decimals: int = 1) -> str:
    """Formatea un número con decimales usando coma.

    Ejemplo: 1234.56 → '1.234,6'  (con decimals=1)
    """
    try:
        formatted = f"{float(value):,.{decimals}f}"
        # Intercambiar coma ↔ punto para formato chileno
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted
    except (ValueError, TypeError):
        return "—"


def fmt_percentage(value, decimals: int = 1) -> str:
    """Formatea un decimal como porcentaje.

    Ejemplo: 0.0868 → '8,7%'
    """
    try:
        pct = float(value) * 100
        formatted = f"{pct:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}%"
    except (ValueError, TypeError):
        return "—"


def fmt_pp(value, decimals: int = 1) -> str:
    """Formatea diferencia de porcentajes en puntos porcentuales.

    Ejemplo: 0.018 → '+1,8 pp'   -0.031 → '-3,1 pp'
    """
    try:
        pp = float(value) * 100
        sign = "+" if pp > 0 else ""
        formatted = f"{pp:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{sign}{formatted} pp"
    except (ValueError, TypeError):
        return "—"


def fmt_variation(value, decimals: int = 1) -> str:
    """Formatea variación porcentual con signo.

    Ejemplo: 0.085 → '+8,5%'   -0.12 → '-12,0%'
    """
    try:
        pct = float(value) * 100
        sign = "+" if pct > 0 else ""
        formatted = f"{pct:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{sign}{formatted}%"
    except (ValueError, TypeError):
        return "—"


def fmt_mt(value) -> str:
    """Formatea metros con unidad.

    Ejemplo: 125000 → '125.000 MT'
    """
    return f"{fmt_integer(value)} MT"


def fmt_kpi_value(value, fmt_type: str) -> str:
    """Formatea un valor KPI según su tipo de formato.

    Args:
        value: Valor numérico.
        fmt_type: 'integer', 'percentage', 'decimal'.
    """
    if fmt_type == "integer":
        return fmt_integer(value)
    elif fmt_type == "percentage":
        return fmt_percentage(value)
    elif fmt_type == "decimal":
        return fmt_decimal(value)
    return str(value)
