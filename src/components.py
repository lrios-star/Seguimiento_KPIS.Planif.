"""
Componentes visuales reutilizables para Streamlit.

Incluye: tarjetas KPI, CSS del dashboard, tablas formateadas,
secciones con estilo profesional.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from config import Colors, KPI_CONFIG
from src.utils import fmt_integer, fmt_percentage, fmt_pp, fmt_variation, fmt_kpi_value


# ---------------------------------------------------------------------------
# CSS global del dashboard
# ---------------------------------------------------------------------------

def inject_custom_css():
    """Inyecta CSS personalizado para aspecto profesional e industrial."""
    st.markdown("""
    <style>
        /* ---- Tipografía ---- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        /* ---- Fondo de la app ---- */
        .stApp {
            background-color: #f0f2f6;
        }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {
            background-color: #1a1f36;
            color: #ffffff;
        }
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown label,
        section[data-testid="stSidebar"] .stMarkdown span,
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
        section[data-testid="stSidebar"] [data-baseweb="select"] span {
            color: #ffffff !important;
        }

        /* ---- Esconder menú hamburguesa y footer ---- */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Ocultar la línea roja de decoración de Streamlit */
        [data-testid="stDecoration"] { display: none !important; }
        
        /* Permitimos que el header se vea para que aparezca el botón de colapsar la sidebar sin fondo blanco */
        header { 
            background: transparent !important; 
            box-shadow: none !important;
        }

        /* ---- Botones en la sidebar (Ej. Actualizar datos) ---- */
        section[data-testid="stSidebar"] .stButton button {
            color: #1a1f36 !important;
            background-color: #ffffff !important;
            border: 1px solid #ffffff !important;
        }
        section[data-testid="stSidebar"] .stButton button p {
            color: #1a1f36 !important;
        }
        section[data-testid="stSidebar"] .stButton button:hover {
            background-color: #e5e7eb !important;
            border-color: #e5e7eb !important;
        }

        /* ---- Botón de colapsar la sidebar ('<' gris) ---- */
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
            fill: #ffffff !important;
            color: #ffffff !important;
        }

        /* ---- Cards KPI ---- */
        .kpi-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 20px 18px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            transition: box-shadow 0.2s ease, transform 0.2s ease;
            height: 100%;
        }
        .kpi-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }
        .kpi-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #6b7280;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #1a1f36;
            line-height: 1.2;
            margin-bottom: 4px;
        }
        .kpi-unit {
            font-size: 14px;
            font-weight: 400;
            color: #6b7280;
            margin-left: 2px;
        }
        .kpi-previous {
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 6px;
        }
        .kpi-variation {
            font-size: 13px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 20px;
            display: inline-block;
        }
        .kpi-variation.positive {
            color: #059669;
            background: #d1fae5;
        }
        .kpi-variation.negative {
            color: #dc2626;
            background: #fee2e2;
        }
        .kpi-variation.neutral {
            color: #6b7280;
            background: #f3f4f6;
        }
        .kpi-interpretation {
            font-size: 11px;
            color: #6b7280;
            margin-top: 4px;
            font-style: italic;
        }

        /* ---- Section headers ---- */
        .section-header {
            background: linear-gradient(135deg, #1a1f36 0%, #2d3555 100%);
            color: #ffffff;
            padding: 16px 24px;
            border-radius: 10px;
            margin: 28px 0 16px 0;
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        /* ---- Dashboard header ---- */
        .dashboard-header {
            background: linear-gradient(135deg, #1a1f36 0%, #2d3555 100%);
            color: #ffffff;
            padding: 28px 32px;
            border-radius: 14px;
            margin-bottom: 24px;
        }
        .dashboard-title {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .dashboard-subtitle {
            font-size: 14px;
            font-weight: 400;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .period-badge {
            display: inline-block;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 6px 14px;
            font-size: 13px;
            color: #e2e8f0;
            margin-right: 10px;
        }
        .period-badge strong {
            color: #ffffff;
            font-weight: 600;
        }

        /* ---- Tablas con DataFrames ---- */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }

        /* ---- Info card ---- */
        .info-card {
            background: #ffffff;
            border-radius: 10px;
            padding: 18px 22px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            margin-bottom: 12px;
        }
        .info-card-label {
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-bottom: 4px;
        }
        .info-card-value {
            font-size: 22px;
            font-weight: 700;
            color: #1a1f36;
        }

        /* ---- Metric highlight ---- */
        .critical-badge {
            background: #fee2e2;
            color: #dc2626;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }
        .safe-badge {
            background: #d1fae5;
            color: #059669;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }

        /* ---- Divider ---- */
        .section-divider {
            border: none;
            height: 1px;
            background: #e2e8f0;
            margin: 24px 0;
        }

        /* Remove default streamlit padding */
        .block-container {
            padding-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header del dashboard
# ---------------------------------------------------------------------------

def render_header(current_label: str, previous_label: str | None):
    """Renderiza el encabezado principal del dashboard."""
    period_html = f'<span class="period-badge">Periodo actual: <strong>{current_label}</strong></span>'
    if previous_label:
        period_html += f'<span class="period-badge">Comparado con: <strong>{previous_label}</strong></span>'

    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">SEGUIMIENTO SEMANAL DE PRODUCCIÓN Y MERMAS</div>
        <div class="dashboard-subtitle">Análisis comparativo del desempeño productivo</div>
        {period_html}
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------

def render_section_header(title: str):
    """Renderiza un encabezado de sección con estilo."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tarjetas KPI
# ---------------------------------------------------------------------------

def render_kpi_card(
    kpi_key: str,
    current_value: float,
    previous_value: float | None = None,
    variation: dict | None = None,
    is_positive: bool | None = None,
    value_color: str | None = None,
):
    """Renderiza una tarjeta KPI individual con variación e interpretación."""
    config = KPI_CONFIG.get(kpi_key, {})
    label = config.get("label", kpi_key)
    unit = config.get("unit", "")
    fmt_type = config.get("format", "integer")

    # Valor formateado
    value_str = fmt_kpi_value(current_value, fmt_type)
    
    value_style = f"color: {value_color} !important;" if value_color else ""

    # Valor anterior
    prev_html = ""
    if previous_value is not None:
        prev_str = fmt_kpi_value(previous_value, fmt_type)
        prev_html = f'<div class="kpi-previous">Anterior: {prev_str}</div>'

    # Variación
    variation_html = ""
    interp_html = ""
    if variation is not None:
        direction = variation.get("direction", "equal")

        if fmt_type == "percentage":
            # Para porcentajes, mostrar la diferencia en puntos porcentuales
            diff_str = fmt_pp(variation["absolute"])
            arrow = "▲" if direction == "up" else "▼" if direction == "down" else "—"
        else:
            abs_diff = variation["absolute"]
            diff_str = fmt_integer(abs(abs_diff))
            if variation["relative"] is not None:
                pct_str = fmt_variation(variation["relative"])
                diff_str = f"{diff_str} ({pct_str})"
            arrow = "▲" if direction == "up" else "▼" if direction == "down" else "—"

        # Clase CSS según si la variación es positiva o negativa para el negocio
        if is_positive is True:
            css_class = "positive"
        elif is_positive is False:
            css_class = "negative"
        else:
            css_class = "neutral"

        variation_html = f'<div class="kpi-variation {css_class}">{arrow} {diff_str}</div>'

        # Interpretación textual
        positive_when = config.get("positive_when", "increase")
        if direction == "up":
            if positive_when == "increase":
                interp = "Mejora respecto al periodo anterior"
            else:
                interp = "Aumento respecto al periodo anterior"
        elif direction == "down":
            if positive_when == "decrease":
                interp = "Mejora respecto al periodo anterior"
            else:
                interp = "Disminución respecto al periodo anterior"
        else:
            interp = "Sin cambios"
        interp_html = f'<div class="kpi-interpretation">{interp}</div>'

    # Unit suffix
    unit_html = f'<span class="kpi-unit">{unit}</span>' if unit and fmt_type != "percentage" else ""

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="{value_style}">{value_str}{unit_html}</div>
        {prev_html}
        {variation_html}
        {interp_html}
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tablas formateadas
# ---------------------------------------------------------------------------

def format_production_table(df: pd.DataFrame) -> pd.DataFrame:
    """Formatea la tabla de producción para visualización."""
    if df.empty:
        return df

    display_df = df.copy()

    # Formatear columnas numéricas
    if "CANTIDAD PLAN MT" in display_df.columns:
        display_df["CANTIDAD PLAN MT"] = display_df["CANTIDAD PLAN MT"].apply(lambda x: fmt_integer(x))
    if "CANTIDAD CIERRE MT" in display_df.columns:
        display_df["CANTIDAD CIERRE MT"] = display_df["CANTIDAD CIERRE MT"].apply(lambda x: fmt_integer(x))
    if "MERMA MT" in display_df.columns:
        display_df["MERMA MT"] = display_df["MERMA MT"].apply(lambda x: fmt_integer(x))
    if "% MERMA" in display_df.columns:
        display_df["% MERMA"] = display_df["% MERMA"].apply(lambda x: fmt_percentage(x))
    if "% MERMA VS PERIODO" in display_df.columns:
        display_df["% MERMA VS PERIODO"] = display_df["% MERMA VS PERIODO"].apply(lambda x: fmt_percentage(x))
    if "FECHA DE CIERRE" in display_df.columns:
        display_df["FECHA DE CIERRE"] = pd.to_datetime(display_df["FECHA DE CIERRE"], errors="coerce").dt.strftime("%d-%m-%Y")
        display_df["FECHA DE CIERRE"] = display_df["FECHA DE CIERRE"].fillna("—")

    return display_df


def format_aggregated_table(df: pd.DataFrame) -> pd.DataFrame:
    """Formatea una tabla agrupada (clientes/productos)."""
    if df.empty:
        return df

    display_df = df.copy()
    if "MT_PLANIFICADOS" in display_df.columns:
        display_df["MT_PLANIFICADOS"] = display_df["MT_PLANIFICADOS"].apply(fmt_integer)
    if "MT_CONCRETADOS" in display_df.columns:
        display_df["MT_CONCRETADOS"] = display_df["MT_CONCRETADOS"].apply(fmt_integer)
    if "MT_MERMA" in display_df.columns:
        display_df["MT_MERMA"] = display_df["MT_MERMA"].apply(fmt_integer)
    if "% MERMA" in display_df.columns:
        display_df["% MERMA"] = display_df["% MERMA"].apply(fmt_percentage)

    # Renombrar columnas para display
    rename_map = {
        "MT_PLANIFICADOS": "MT PLANIF",
        "MT_CONCRETADOS": "MT CONCRET",
        "MT_MERMA": "MT MERMA",
    }
    display_df = display_df.rename(columns=rename_map)

    return display_df
