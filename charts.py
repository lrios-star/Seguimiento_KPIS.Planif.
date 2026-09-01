"""
Gráficos interactivos con Plotly para el dashboard de producción y mermas.
"""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config import Colors
from src.utils import fmt_integer, fmt_percentage

# ---------------------------------------------------------------------------
# Layout base
# ---------------------------------------------------------------------------
_BASE_LAYOUT = dict(
    font=dict(family="Inter, -apple-system, sans-serif", color=Colors.TEXT_PRIMARY),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11),
    ),
)


def _apply_base_layout(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    """Aplica el layout base a cualquier gráfico."""
    fig.update_layout(
        **_BASE_LAYOUT,
        title=dict(text=title, font=dict(size=14, color=Colors.TEXT_PRIMARY), x=0, xanchor="left"),
        height=height,
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor=Colors.BORDER_LIGHT,
        tickfont=dict(size=11),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=Colors.BORDER_LIGHT,
        gridwidth=0.5,
        showline=False,
        tickfont=dict(size=11),
    )
    return fig


# ---------------------------------------------------------------------------
# Gráficos de evolución / tendencia
# ---------------------------------------------------------------------------

def chart_ops_cerradas(df_hist: pd.DataFrame) -> go.Figure:
    """Gráfico de barras de OP cerradas por periodo."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_hist["periodo"],
        y=df_hist["ops_cerradas"],
        marker_color=Colors.CHART_BLUE,
        text=df_hist["ops_cerradas"].apply(fmt_integer),
        textposition="outside",
        textfont=dict(size=12, color=Colors.TEXT_PRIMARY),
        hovertemplate="Periodo: %{x}<br>OP cerradas: %{text}<extra></extra>",
    ))
    fig = _apply_base_layout(fig, "OP Cerradas por Periodo")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Cantidad de OP")
    return fig


def chart_mt_plan_vs_concretados(df_hist: pd.DataFrame) -> go.Figure:
    """Gráfico de barras agrupadas: MT planificados vs concretados."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_hist["periodo"],
        y=df_hist["mt_planificados"],
        name="Planificados",
        marker_color=Colors.CHART_BLUE_LIGHT,
        customdata=df_hist["mt_planificados"].apply(lambda x: f"{fmt_integer(x)} MT"),
        hovertemplate="Planificados: %{customdata}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df_hist["periodo"],
        y=df_hist["mt_concretados"],
        name="Concretados",
        marker_color=Colors.CHART_BLUE,
        customdata=df_hist["mt_concretados"].apply(lambda x: f"{fmt_integer(x)} MT"),
        hovertemplate="Concretados: %{customdata}<extra></extra>",
    ))
    fig = _apply_base_layout(fig, "MT Planificados vs Concretados")
    fig.update_xaxes(type="category")
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Metros (MT)")
    return fig


def chart_mt_merma(df_hist: pd.DataFrame) -> go.Figure:
    """Gráfico de barras de MT de merma por periodo."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_hist["periodo"],
        y=df_hist["mt_merma"],
        marker_color=Colors.CHART_AMBER,
        text=df_hist["mt_merma"].apply(fmt_integer),
        textposition="outside",
        textfont=dict(size=11, color=Colors.TEXT_PRIMARY),
        hovertemplate="Periodo: %{x}<br>MT Merma: %{text}<extra></extra>",
    ))
    fig = _apply_base_layout(fig, "Metros de Merma por Periodo")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Metros (MT)")
    return fig


def chart_pct_merma(df_hist: pd.DataFrame) -> go.Figure:
    """Gráfico de línea del % de merma por periodo."""
    pct_values = df_hist["pct_merma"] * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_hist["periodo"],
        y=pct_values,
        mode="lines+markers+text",
        marker=dict(size=10, color=Colors.CHART_RED),
        line=dict(color=Colors.CHART_RED, width=2.5),
        text=df_hist["pct_merma"].apply(fmt_percentage),
        textposition="top center",
        textfont=dict(size=11),
        customdata=df_hist["ops_cerradas"],
        hovertemplate="Periodo: %{x}<br>% Merma: %{text}<br>N° de OPs: %{customdata}<extra></extra>",
    ))
    fig = _apply_base_layout(fig, "% de Merma por Periodo")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="% Merma")
    return fig


def chart_pct_ops_merma_5(df_hist: pd.DataFrame) -> go.Figure:
    """Gráfico de línea del % de OP con merma >= 5%."""
    pct_values = df_hist["pct_ops_merma_5"] * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_hist["periodo"],
        y=pct_values,
        mode="lines+markers+text",
        marker=dict(size=10, color=Colors.CHART_PURPLE),
        line=dict(color=Colors.CHART_PURPLE, width=2.5),
        text=df_hist["pct_ops_merma_5"].apply(fmt_percentage),
        textposition="top center",
        textfont=dict(size=11),
        customdata=df_hist["ops_merma_5"],
        hovertemplate="Periodo: %{x}<br>% OP ≥5%%: %{text}<br>N° de OPs: %{customdata}<extra></extra>",
    ))
    fig = _apply_base_layout(fig, "% OP con Merma ≥5% por Periodo")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="% OP con Merma ≥5%")
    return fig


# ---------------------------------------------------------------------------
# Gráficos de análisis
# ---------------------------------------------------------------------------

def chart_top_clientes_merma(df_agg: pd.DataFrame, n: int = 10) -> go.Figure:
    """Gráfico de barras horizontales: top clientes por MT de merma."""
    df_top = df_agg.head(n).sort_values("MT_MERMA", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_top["MT_MERMA"],
        y=df_top["CLIENTE"],
        orientation="h",
        marker_color=Colors.CHART_BLUE,
        text=df_top["MT_MERMA"].apply(fmt_integer),
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="Cliente: %{y}<br>MT Merma: %{text}<extra></extra>",
    ))
    fig = _apply_base_layout(fig, f"Top {min(n, len(df_top))} Clientes por MT de Merma", height=max(300, len(df_top) * 35 + 80))
    fig.update_xaxes(title_text="Metros de Merma (MT)")
    fig.update_yaxes(showgrid=False)
    fig.update_layout(margin=dict(l=120))
    return fig


def chart_top_productos_merma(df_agg: pd.DataFrame, n: int = 10) -> go.Figure:
    """Gráfico de barras horizontales: top productos por MT de merma."""
    df_top = df_agg.head(n).sort_values("MT_MERMA", ascending=True)

    # Truncar nombres largos
    df_top = df_top.copy()
    df_top["PRODUCTO_SHORT"] = df_top["PRODUCTO"].apply(
        lambda x: x[:40] + "..." if isinstance(x, str) and len(x) > 40 else x
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_top["MT_MERMA"],
        y=df_top["PRODUCTO_SHORT"],
        orientation="h",
        marker_color=Colors.CHART_TEAL,
        text=df_top["MT_MERMA"].apply(fmt_integer),
        textposition="outside",
        textfont=dict(size=11),
        customdata=df_top["PRODUCTO"],
        hovertemplate="Producto: %{customdata}<br>MT Merma: %{text}<extra></extra>",
    ))
    fig = _apply_base_layout(fig, f"Top {min(n, len(df_top))} Productos por MT de Merma", height=max(300, len(df_top) * 38 + 80))
    fig.update_xaxes(title_text="Metros de Merma (MT)")
    fig.update_yaxes(showgrid=False)
    fig.update_layout(margin=dict(l=200))
    return fig


def chart_merma_distribution(df: pd.DataFrame) -> go.Figure:
    """Histograma de distribución del % de merma en las OP."""
    pct_values = df["% MERMA"] * 100

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=pct_values,
        nbinsx=20,
        marker_color=Colors.CHART_BLUE,
        marker_line=dict(color=Colors.BG_CARD, width=1),
        hovertemplate="Rango: %{x:.1f}%<br>Cantidad: %{y}<extra></extra>",
    ))

    # Línea de umbral 5%
    fig.add_vline(
        x=5, line_dash="dash", line_color=Colors.CHART_RED, line_width=2,
        annotation_text="Umbral 5%",
        annotation_position="top right",
        annotation_font=dict(size=11, color=Colors.CHART_RED),
    )

    fig = _apply_base_layout(fig, "Distribución del % de Merma por OP")
    fig.update_xaxes(title_text="% Merma", ticksuffix="%")
    fig.update_yaxes(title_text="Cantidad de OP")
    return fig
