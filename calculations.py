"""
Cálculos de indicadores de producción y mermas.

Reconstruye todos los KPIs desde los datos detallados con Pandas,
sin depender de las fórmulas del Excel.
"""
from __future__ import annotations

import pandas as pd

from config import MERMA_CRITICA_THRESHOLD, KPI_CONFIG


def calculate_indicators(df: pd.DataFrame) -> dict:
    """Calcula los indicadores KPI desde la tabla de datos.

    Args:
        df: DataFrame con las columnas de producción.

    Returns:
        Dict con los indicadores calculados.
    """
    if df.empty:
        return {
            "ops_cerradas": 0,
            "mt_planificados": 0,
            "mt_concretados": 0,
            "mt_merma": 0,
            "pct_merma": 0,
            "ops_merma_5": 0,
            "pct_ops_merma_5": 0,
        }

    n_ops = len(df)
    mt_plan = df["CANTIDAD PLAN MT"].sum()
    mt_cierre = df["CANTIDAD CIERRE MT"].sum()
    mt_merma = df["MERMA MT"].sum()
    pct_merma = mt_merma / mt_plan if mt_plan > 0 else 0
    ops_criticas = (df["% MERMA"] >= MERMA_CRITICA_THRESHOLD).sum()
    pct_ops_criticas = ops_criticas / n_ops if n_ops > 0 else 0

    return {
        "ops_cerradas": n_ops,
        "mt_planificados": mt_plan,
        "mt_concretados": mt_cierre,
        "mt_merma": mt_merma,
        "pct_merma": pct_merma,
        "ops_merma_5": int(ops_criticas),
        "pct_ops_merma_5": pct_ops_criticas,
    }


def calculate_variation(current: float, previous: float) -> dict:
    """Calcula la variación entre dos valores.

    Returns:
        Dict con:
        - "absolute": diferencia absoluta
        - "relative": variación porcentual (None si previous == 0)
        - "direction": "up", "down" o "equal"
    """
    diff = current - previous
    if previous != 0:
        relative = diff / abs(previous)
    else:
        relative = None

    if diff > 0:
        direction = "up"
    elif diff < 0:
        direction = "down"
    else:
        direction = "equal"

    return {
        "absolute": diff,
        "relative": relative,
        "direction": direction,
    }


def is_variation_positive(kpi_key: str, direction: str) -> bool | None:
    """Determina si una variación es positiva según la naturaleza del KPI.

    Args:
        kpi_key: Clave del KPI en KPI_CONFIG.
        direction: "up", "down" o "equal".

    Returns:
        True si la variación es positiva, False si negativa, None si neutra.
    """
    if direction == "equal":
        return None

    config = KPI_CONFIG.get(kpi_key, {})
    positive_when = config.get("positive_when", "increase")

    if positive_when == "increase":
        return direction == "up"
    else:  # decrease
        return direction == "down"


def calculate_all_kpi_variations(current_ind: dict, previous_ind: dict) -> dict:
    """Calcula las variaciones de todos los KPIs entre dos periodos.

    Returns:
        Dict con la estructura:
        {
            "kpi_key": {
                "current": valor,
                "previous": valor,
                "variation": {...},
                "is_positive": bool | None,
            },
            ...
        }
    """
    results = {}
    for kpi_key in KPI_CONFIG:
        cur = current_ind.get(kpi_key, 0)
        prev = previous_ind.get(kpi_key, 0)
        variation = calculate_variation(cur, prev)
        is_positive = is_variation_positive(kpi_key, variation["direction"])

        results[kpi_key] = {
            "current": cur,
            "previous": prev,
            "variation": variation,
            "is_positive": is_positive,
        }
    return results


def get_critical_ops(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra las OP con merma >= umbral crítico.

    Returns:
        DataFrame filtrado y ordenado por % MERMA descendente.
    """
    if df.empty:
        return df
    critical = df[df["% MERMA"] >= MERMA_CRITICA_THRESHOLD].copy()
    critical = critical.sort_values("% MERMA", ascending=False)
    return critical.reset_index(drop=True)


def get_top_by_merma(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Obtiene las top N OP por MT de merma.

    Returns:
        DataFrame ordenado por MERMA MT descendente.
    """
    if df.empty:
        return df
    return df.nlargest(n, "MERMA MT").reset_index(drop=True)


def aggregate_by_column(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Agrega datos por una columna (CLIENTE o PRODUCTO).

    Returns:
        DataFrame agrupado con totales y porcentaje de merma.
    """
    if df.empty:
        return pd.DataFrame()

    agg = df.groupby(group_col, dropna=False).agg(
        OP=("OP", "count"),
        MT_PLANIFICADOS=("CANTIDAD PLAN MT", "sum"),
        MT_CONCRETADOS=("CANTIDAD CIERRE MT", "sum"),
        MT_MERMA=("MERMA MT", "sum"),
    ).reset_index()

    agg["% MERMA"] = agg["MT_MERMA"] / agg["MT_PLANIFICADOS"].replace(0, float("nan"))
    agg["% MERMA"] = agg["% MERMA"].fillna(0)
    agg = agg.sort_values("MT_MERMA", ascending=False).reset_index(drop=True)

    return agg


def compare_ops_between_periods(
    df_current: pd.DataFrame,
    df_previous: pd.DataFrame,
) -> dict:
    """Compara las OP entre dos periodos.

    Returns:
        Dict con:
        - "new_ops": OP presentes solo en el periodo actual
        - "common_ops": OP presentes en ambos periodos
        - "removed_ops": OP presentes solo en el periodo anterior
        - "comparison_df": DataFrame con la comparación detallada de OP comunes
    """
    current_ops = set(df_current["OP"].unique())
    previous_ops = set(df_previous["OP"].unique())

    new_ops = current_ops - previous_ops
    common_ops = current_ops & previous_ops
    removed_ops = previous_ops - current_ops

    result = {
        "new_ops": sorted(new_ops),
        "common_ops": sorted(common_ops),
        "removed_ops": sorted(removed_ops),
        "new_count": len(new_ops),
        "common_count": len(common_ops),
        "removed_count": len(removed_ops),
    }

    # Construir tabla comparativa de OP comunes
    if common_ops:
        cur = df_current[df_current["OP"].isin(common_ops)].set_index("OP")
        prev = df_previous[df_previous["OP"].isin(common_ops)].set_index("OP")

        comparison = pd.DataFrame({
            "OP": sorted(common_ops),
        }).set_index("OP")

        comparison["% MERMA ACTUAL"] = cur["% MERMA"]
        comparison["% MERMA ANTERIOR"] = prev["% MERMA"]
        comparison["DIFF MERMA"] = comparison["% MERMA ACTUAL"] - comparison["% MERMA ANTERIOR"]
        comparison = comparison.reset_index()
        comparison = comparison.sort_values("DIFF MERMA", ascending=False)
        result["comparison_df"] = comparison
    else:
        result["comparison_df"] = pd.DataFrame()

    return result


def build_historical_series(all_data: dict, periods: list) -> pd.DataFrame:
    """Construye una serie histórica con los indicadores de cada periodo.

    Args:
        all_data: Dict {label: DataFrame} por periodo.
        periods: Lista de periodos ordenados cronológicamente.

    Returns:
        DataFrame con una fila por periodo y columnas de indicadores.
    """
    rows = []
    for period in periods:
        label = period["label"]
        if label in all_data:
            ind = calculate_indicators(all_data[label])
            ind["periodo"] = label
            ind["fecha"] = period["period_date"]
            rows.append(ind)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.sort_values("fecha").reset_index(drop=True)
    return df
