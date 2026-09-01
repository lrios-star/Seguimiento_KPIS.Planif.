"""
Dashboard de Seguimiento Semanal de Producción y Mermas.

Aplicación principal de Streamlit que integra la carga de datos,
cálculos de indicadores, visualizaciones y componentes UI.

Ejecutar con:
    streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# Asegurar que el directorio del proyecto esté en el path
_PROJECT_DIR = Path(__file__).resolve().parent
if str(_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(_PROJECT_DIR))

from config import PAGE_TITLE, PAGE_ICON, LAYOUT, EXCEL_PATH, KPI_CONFIG, MERMA_CRITICA_THRESHOLD, Colors
from src.data_loader import load_all_periods
from src.calculations import (
    calculate_indicators,
    calculate_all_kpi_variations,
    get_critical_ops,
    get_top_by_merma,
    aggregate_by_column,
    compare_ops_between_periods,
    build_historical_series,
)
from src.charts import (
    chart_ops_cerradas,
    chart_mt_plan_vs_concretados,
    chart_mt_merma,
    chart_pct_merma,
    chart_pct_ops_merma_5,
    chart_top_clientes_merma,
    chart_top_productos_merma,
    chart_merma_distribution,
)
from src.components import (
    inject_custom_css,
    render_header,
    render_section_header,
    render_kpi_card,
    format_production_table,
    format_aggregated_table,
)
from src.utils import fmt_integer, fmt_percentage

# =========================================================================
# Page config
# =========================================================================
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded",
)

inject_custom_css()


# =========================================================================
# Data loading (cached)
# =========================================================================
@st.cache_data(show_spinner="Cargando datos del Excel...")
def load_data():
    """Carga todos los datos del Excel con caché."""
    return load_all_periods()


# =========================================================================
# Main
# =========================================================================
def main():
    # ---- Verificar que exista el archivo Excel ----
    if not EXCEL_PATH.exists():
        st.error(
            f"No se encontró el archivo Excel en:\n\n`{EXCEL_PATH}`\n\n"
            "Por favor, verifica que el archivo `dataset.xlsx` esté en la carpeta del proyecto."
        )
        return

    # ---- Cargar datos ----
    all_data = load_all_periods()
    periods = all_data["periods"]
    data = all_data["data"]
    summaries = all_data["summaries"]
    details = all_data.get("details", {})
    errors = all_data.get("errors", {})

    # ---- Validar que existan periodos ----
    if not periods:
        st.error(
            "No se encontraron hojas con formato de periodo válido (DD-MM) en el archivo Excel.\n\n"
            "Verifica que las hojas tengan nombres como `17-08`, `24-08`, etc."
        )
        return

    # Mostrar errores de carga si los hay
    for label, error in errors.items():
        st.warning(f"Error al procesar el periodo {label}: {error}")

    # ---- Determinar periodos disponibles ----
    period_labels = [p["label"] for p in periods if p["label"] in data]

    if not period_labels:
        st.error("No se pudieron cargar datos de ningún periodo.")
        return

    # Periodo actual = el más reciente, anterior = el segundo más reciente
    current_label = period_labels[-1]
    previous_label = period_labels[-2] if len(period_labels) >= 2 else None

    # ================================================================
    # SIDEBAR
    # ================================================================
    with st.sidebar:
        logo_path = Path(__file__).resolve().parent / "LOGO.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")

        # Selector de periodo actual
        current_label = st.selectbox(
            "Periodo actual",
            options=period_labels,
            index=len(period_labels) - 1,
        )

        # Selector de periodo de comparación
        comparison_options = [l for l in period_labels if l != current_label]
        if comparison_options:
            # Default: el periodo inmediatamente anterior al seleccionado
            current_idx = period_labels.index(current_label)
            default_prev_idx = max(0, current_idx - 1)
            # Buscar el default en comparison_options
            if default_prev_idx < len(period_labels) and period_labels[default_prev_idx] in comparison_options:
                default_comp = comparison_options.index(period_labels[default_prev_idx])
            else:
                default_comp = len(comparison_options) - 1

            previous_label = st.selectbox(
                "Periodo de comparación",
                options=comparison_options,
                index=default_comp,
            )
        else:
            previous_label = None
            st.info("Solo hay un periodo disponible.")

        st.markdown("---")

        # Obtener datos del periodo actual para los filtros
        df_current = data.get(current_label, pd.DataFrame())

        # Filtro de cliente
        if not df_current.empty and "CLIENTE" in df_current.columns:
            clientes = sorted(df_current["CLIENTE"].dropna().unique().tolist())
            selected_clientes = st.multiselect("Cliente", clientes)
        else:
            selected_clientes = []

        # Filtro de producto
        if not df_current.empty and "PRODUCTO" in df_current.columns:
            productos = sorted(df_current["PRODUCTO"].dropna().unique().tolist())
            selected_productos = st.multiselect("Producto", productos)
        else:
            selected_productos = []

        # Filtro de Fecha de Cierre
        if not df_current.empty and "FECHA DE CIERRE" in df_current.columns:
            fechas = sorted([str(f)[:10] for f in df_current["FECHA DE CIERRE"].dropna().unique()])
            selected_fechas = st.multiselect("Fecha de Cierre", fechas)
        else:
            selected_fechas = []

        st.markdown("---")
        st.markdown(
            f"<div style='font-size:11px; color:#94a3b8;'>"
            f"Periodos detectados: {len(period_labels)}<br>"
            f"Archivo: dataset.xlsx"
            f"</div><br>",
            unsafe_allow_html=True,
        )

        # Botón actualizar datos al final
        if st.button("🔄  Actualizar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ================================================================
    # Aplicar filtros
    # ================================================================
    df_current = data.get(current_label, pd.DataFrame()).copy()
    df_previous = data.get(previous_label, pd.DataFrame()).copy() if previous_label else pd.DataFrame()

    def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        filtered = df.copy()
        if selected_clientes:
            filtered = filtered[filtered["CLIENTE"].isin(selected_clientes)]
        if selected_productos:
            filtered = filtered[filtered["PRODUCTO"].isin(selected_productos)]
        if selected_fechas:
            filtered = filtered[filtered["FECHA DE CIERRE"].astype(str).str[:10].isin(selected_fechas)]
        return filtered

    df_current_filtered = apply_filters(df_current)
    df_previous_filtered = apply_filters(df_previous) if not df_previous.empty else pd.DataFrame()

    # ================================================================
    # HEADER
    # ================================================================
    render_header(current_label, previous_label)

    # ================================================================
    # BLOQUE 1: KPIs PRINCIPALES
    # ================================================================
    render_section_header("INDICADORES PRINCIPALES")

    current_ind = calculate_indicators(df_current_filtered)
    previous_ind = calculate_indicators(df_previous_filtered) if not df_previous_filtered.empty else None

    if previous_ind:
        kpi_vars = calculate_all_kpi_variations(current_ind, previous_ind)
    else:
        kpi_vars = None

    # Renderizar KPIs en 2 filas de 3
    kpi_keys = list(KPI_CONFIG.keys())
    row1_keys = kpi_keys[:3]
    row2_keys = kpi_keys[3:]

    for row_keys in [row1_keys, row2_keys]:
        cols = st.columns(len(row_keys))
        for col, kpi_key in zip(cols, row_keys):
            with col:
                value_color = None
                if kpi_key == "pct_merma":
                    val = kpi_vars[kpi_key]["current"] if kpi_vars and kpi_key in kpi_vars else current_ind.get(kpi_key, 0)
                    if val >= MERMA_CRITICA_THRESHOLD:
                        value_color = Colors.NEGATIVE
                        
                if kpi_vars and kpi_key in kpi_vars:
                    kv = kpi_vars[kpi_key]
                    render_kpi_card(
                        kpi_key=kpi_key,
                        current_value=kv["current"],
                        previous_value=kv["previous"],
                        variation=kv["variation"],
                        is_positive=kv["is_positive"],
                        value_color=value_color
                    )
                else:
                    render_kpi_card(
                        kpi_key=kpi_key,
                        current_value=current_ind.get(kpi_key, 0),
                        value_color=value_color
                    )

    # ================================================================
    # BLOQUE 2: EVOLUCIÓN DEL DESEMPEÑO
    # ================================================================
    # Usar datos sin filtros para la serie histórica
    df_hist = build_historical_series(data, periods)

    if not df_hist.empty and len(df_hist) >= 2:
        render_section_header("EVOLUCIÓN DEL DESEMPEÑO")

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(chart_ops_cerradas(df_hist), use_container_width=True)
        with col2:
            st.plotly_chart(chart_mt_plan_vs_concretados(df_hist), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(chart_mt_merma(df_hist), use_container_width=True)
        with col4:
            st.plotly_chart(chart_pct_merma(df_hist), use_container_width=True)

        st.plotly_chart(chart_pct_ops_merma_5(df_hist), use_container_width=True)

    elif not df_hist.empty and len(df_hist) == 1:
        pass

      # ================================================================
    # OP CRÍTICAS (merma >= 5%)
    # ================================================================
    render_section_header("OPS con MERMAS ≥ 5% (PERIODO ACTUAL)")

    critical_ops = get_critical_ops(df_current_filtered)

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-label">Cantidad de OP</div>
            <div class="info-card-value">{len(critical_ops)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        total_ops = len(df_current_filtered)
        pct_critical = len(critical_ops) / total_ops * 100 if total_ops > 0 else 0
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-label">% sobre el Total</div>
            <div class="info-card-value">{pct_critical:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col_info3:
        mt_merma_critica = critical_ops["MERMA MT"].sum() if not critical_ops.empty else 0
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-label">MT Merma (OP ≥ 5%)</div>
            <div class="info-card-value">{fmt_integer(mt_merma_critica)}</div>
        </div>
        """, unsafe_allow_html=True)

    if not critical_ops.empty:
        display_cols = ["OP", "PRODUCTO", "CLIENTE", "CANTIDAD PLAN MT", "CANTIDAD CIERRE MT", "MERMA MT", "% MERMA"]
        display_cols = [c for c in display_cols if c in critical_ops.columns]
        formatted_critical = format_production_table(critical_ops[display_cols])
        st.dataframe(formatted_critical, use_container_width=True, hide_index=True, height=min(len(formatted_critical) * 38 + 40, 500))
    else:
        st.success("No hay OP con merma ≥ 5% en el periodo seleccionado.")

    # ================================================================
    # ANÁLISIS POR CLIENTE
    # ================================================================
    render_section_header("ANÁLISIS POR CLIENTE")

    df_clientes = aggregate_by_column(df_current_filtered, "CLIENTE")
    if not df_clientes.empty:
        col_chart, col_table = st.columns([1, 1])
        with col_chart:
            st.plotly_chart(chart_top_clientes_merma(df_clientes, n=10), use_container_width=True)
        with col_table:
            st.markdown("##### Detalle por Cliente")
            formatted_clientes = format_aggregated_table(df_clientes)
            st.dataframe(formatted_clientes, use_container_width=True, hide_index=True, height=min(len(formatted_clientes) * 38 + 40, 420))

    # ================================================================
    # ANÁLISIS POR PRODUCTO
    # ================================================================
    render_section_header("ANÁLISIS POR PRODUCTO")

    df_productos = aggregate_by_column(df_current_filtered, "PRODUCTO")
    if not df_productos.empty:
        col_chart2, col_table2 = st.columns([1, 1])
        with col_chart2:
            st.plotly_chart(chart_top_productos_merma(df_productos, n=10), use_container_width=True)
        with col_table2:
            st.markdown("##### Detalle por Producto")
            formatted_productos = format_aggregated_table(df_productos)
            st.dataframe(formatted_productos, use_container_width=True, hide_index=True, height=min(len(formatted_productos) * 38 + 40, 420))

# ================================================================
    # DETALLE DE OPS CERRADAS (PERIODO ACTUAL)
    # ================================================================
    render_section_header("DETALLE DE OPS CERRADAS (PERIODO ACTUAL)")

    if not df_current_filtered.empty:
        display_cols = [
            "OP", "PRODUCTO", "CLIENTE", "FECHA DE CIERRE",
            "CANTIDAD PLAN MT", "CANTIDAD CIERRE MT", "MERMA MT",
            "% MERMA", "% MERMA VS PERIODO",
        ]
        display_cols = [c for c in display_cols if c in df_current_filtered.columns]
        formatted_detail = format_production_table(df_current_filtered[display_cols])
        st.dataframe(
            formatted_detail,
            use_container_width=True,
            hide_index=True,
            height=min(len(formatted_detail) * 38 + 40, 650),
        )
        
        # --- Detalles de merma expansibles ---
        df_details = details.get(current_label)
        if df_details is not None and not df_details.empty:
            render_section_header("DETALLE DE MERMAS - OPS MAS RELEVANTES (PERIODO ACTUAL)")
            
            # Limpiar OP en ambos DataFrames para asegurar cruce y evitar el ".0"
            df_curr_clean = df_current_filtered.copy()
            if "OP" in df_curr_clean.columns:
                df_curr_clean["OP_clean"] = df_curr_clean["OP"].apply(
                    lambda x: f"{int(float(x))}" if pd.notna(x) and str(x).replace('.','',1).isdigit() else str(x)
                )
                
            df_details_clean = df_details.copy()
            if "OP" in df_details_clean.columns:
                df_details_clean["OP_clean"] = df_details_clean["OP"].apply(
                    lambda x: f"{int(float(x))}" if pd.notna(x) and str(x).replace('.','',1).isdigit() else str(x)
                )

            ops_with_details = df_curr_clean[df_curr_clean["OP_clean"].isin(df_details_clean["OP_clean"])].copy()
            
            if not ops_with_details.empty:
                for _, row in ops_with_details.iterrows():
                    op = row["OP_clean"]
                    producto = row.get("PRODUCTO", "Desconocido")
                    pct_merma = row.get("% MERMA", 0)
                    pct_str = fmt_percentage(pct_merma)
                    
                    with st.expander(f"OP {op} | {producto} | {pct_str} merma"):
                        op_details = df_details_clean[df_details_clean["OP_clean"] == op].copy()
                        if "OP_clean" in op_details.columns:
                            op_details = op_details.drop(columns=["OP_clean"])
                            
                        op_details = op_details.dropna(how="all", axis=1) # Limpiar columnas vacías
                        
                        # Formatear la columna OP visible sin el ".0"
                        if "OP" in op_details.columns:
                            op_details["OP"] = op_details["OP"].apply(
                                lambda x: f"{int(float(x))}" if pd.notna(x) and str(x).replace('.','',1).isdigit() else str(x) if pd.notna(x) else ""
                            )

                        # Formatear números
                        for col in ["Cantidad Desperdicio", "TOTAL"]:
                            if col in op_details.columns:
                                op_details[col] = op_details[col].apply(lambda x: fmt_integer(x) if pd.notna(x) and str(x).strip() != "" else "")
                        if "% " in op_details.columns:
                            op_details["% "] = op_details["% "].apply(lambda x: fmt_percentage(x) if pd.notna(x) and str(x).strip() != "" else "")
                        
                        # Limpiar celdas vacías
                        op_details = op_details.fillna("")
                        
                        # Emular "Celdas Combinadas" solo para los datos generales de la OP
                        if len(op_details) > 1:
                            # Removemos "% " de esta lista para que mantenga sus valores en cada fila
                            merge_cols = ["OP", "PRODUCTO", "TOTAL", "MT / UN", "MT/UN", "Cantidad Desperdicio Total"]
                            for c in merge_cols:
                                if c in op_details.columns:
                                    first_val = op_details[c].replace("", pd.NA).dropna().first_valid_index()
                                    if first_val is not None:
                                        val_to_keep = op_details.at[first_val, c]
                                        op_details[c] = ""
                                        op_details.iloc[0, op_details.columns.get_loc(c)] = val_to_keep
                        st.dataframe(op_details, use_container_width=True, hide_index=True)
        else:
            st.info("No hay detalles de merma disponibles para este periodo.")
    else:
        st.info("No hay datos para mostrar con los filtros seleccionados.") 


if __name__ == "__main__":
    main()
