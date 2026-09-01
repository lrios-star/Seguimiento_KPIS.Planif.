"""
Configuración global del dashboard de producción y mermas.
Centraliza constantes, paleta de colores, formato y parámetros reutilizables.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent
EXCEL_FILENAME = "dataset.xlsx"
EXCEL_PATH = PROJECT_DIR / EXCEL_FILENAME

# ---------------------------------------------------------------------------
# Columnas esperadas en la tabla de datos de cada hoja
# ---------------------------------------------------------------------------
EXPECTED_COLUMNS = [
    "OP",
    "PRODUCTO",
    "CLIENTE",
    "FECHA DE CIERRE",
    "CANTIDAD PLAN MT",
    "CANTIDAD CIERRE MT",
    "MERMA MT",
    "% MERMA",
    "% MERMA VS PERIODO",
]

# Columnas numéricas que se convierten con pd.to_numeric
NUMERIC_COLUMNS = [
    "CANTIDAD PLAN MT",
    "CANTIDAD CIERRE MT",
    "MERMA MT",
    "% MERMA",
    "% MERMA VS PERIODO",
]

# ---------------------------------------------------------------------------
# Nombres amigables de los indicadores en el resumen lateral del Excel
# ---------------------------------------------------------------------------
SUMMARY_LABELS = {
    "OPS CERRADAS": "ops_cerradas",
    "MT PLANIF": "mt_planificados",
    "MT CONCRETADOS": "mt_concretados",
    "MT MERMA": "mt_merma",
    "% MERMA PERIODO": "pct_merma",
    "OPS CON MERMA >=5%": "ops_merma_5",
    "% OPS CON MERMA >=5%": "pct_ops_merma_5",
}

# ---------------------------------------------------------------------------
# Umbral de merma crítica
# ---------------------------------------------------------------------------
MERMA_CRITICA_THRESHOLD = 0.05  # 5 %

# ---------------------------------------------------------------------------
# Paleta de colores — estilo industrial / corporativo
# ---------------------------------------------------------------------------
class Colors:
    """Paleta centralizada de colores."""
    # Fondos
    BG_PAGE = "#f0f2f6"
    BG_CARD = "#ffffff"
    BG_SIDEBAR = "#1a1f36"

    # Texto
    TEXT_PRIMARY = "#1a1f36"
    TEXT_SECONDARY = "#6b7280"
    TEXT_LIGHT = "#ffffff"
    TEXT_MUTED = "#9ca3af"

    # Acentos
    PRIMARY = "#2563eb"       # Azul principal
    PRIMARY_DARK = "#1d4ed8"
    PRIMARY_LIGHT = "#dbeafe"

    # Indicadores
    POSITIVE = "#059669"      # Verde — mejora
    POSITIVE_BG = "#d1fae5"
    NEGATIVE = "#dc2626"      # Rojo — empeora
    NEGATIVE_BG = "#fee2e2"
    WARNING = "#d97706"       # Ámbar — advertencia
    WARNING_BG = "#fef3c7"
    NEUTRAL = "#6b7280"       # Gris — sin cambio
    NEUTRAL_BG = "#f3f4f6"

    # Gráficos
    CHART_BLUE = "#2563eb"
    CHART_BLUE_LIGHT = "#93c5fd"
    CHART_GREEN = "#059669"
    CHART_RED = "#dc2626"
    CHART_AMBER = "#d97706"
    CHART_GRAY = "#9ca3af"
    CHART_PURPLE = "#7c3aed"
    CHART_TEAL = "#0d9488"
    CHART_SEQUENCE = [
        "#2563eb", "#059669", "#d97706", "#dc2626",
        "#7c3aed", "#0d9488", "#ec4899", "#f59e0b",
    ]

    # Bordes
    BORDER_LIGHT = "#e5e7eb"
    BORDER_CARD = "#e2e8f0"

# ---------------------------------------------------------------------------
# Configuración de KPIs
# ---------------------------------------------------------------------------
# positive_when: "increase" si subir es bueno, "decrease" si bajar es bueno
KPI_CONFIG = {
    "ops_cerradas": {
        "label": "OP CERRADAS",
        "unit": "",
        "format": "integer",
        "positive_when": "increase",
        "description": "Órdenes de producción cerradas en el periodo",
    },
    "mt_planificados": {
        "label": "MT PLANIFICADOS",
        "unit": "MT",
        "format": "integer",
        "positive_when": "increase",
        "description": "Metros totales planificados",
    },
    "mt_concretados": {
        "label": "MT CONCRETADOS",
        "unit": "MT",
        "format": "integer",
        "positive_when": "increase",
        "description": "Metros totales concretados",
    },
    "mt_merma": {
        "label": "MT MERMA",
        "unit": "MT",
        "format": "integer",
        "positive_when": "decrease",
        "description": "Metros totales de merma",
    },
    "pct_merma": {
        "label": "% MERMA",
        "unit": "%",
        "format": "percentage",
        "positive_when": "decrease",
        "description": "Porcentaje de merma del periodo",
    },
    "pct_ops_merma_5": {
        "label": "% OP MERMA ≥5%",
        "unit": "%",
        "format": "percentage",
        "positive_when": "decrease",
        "description": "Porcentaje de OP con merma mayor o igual a 5%",
    },
}

# ---------------------------------------------------------------------------
# Streamlit page config
# ---------------------------------------------------------------------------
PAGE_TITLE = "Seguimiento de Producción y Mermas"
PAGE_ICON = "📊"
LAYOUT = "wide"
