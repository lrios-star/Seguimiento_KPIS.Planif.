# Seguimiento Semanal de Producción y Mermas

Dashboard profesional para el análisis comparativo del desempeño productivo, construido con Streamlit.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en el navegador.

## Actualización Semanal

Para incorporar una nueva semana de datos:

1. Abrir el archivo `dataset.xlsx`.
2. Agregar una nueva hoja con el nombre en formato `DD-MM` (ej: `31-08`, `07-09`).
3. Mantener exactamente el mismo formato de columnas que las hojas existentes.
4. Guardar el archivo.
5. En el dashboard, presionar **Actualizar datos** o recargar la página.

El dashboard detectará automáticamente la nueva hoja y la usará como periodo actual.

## Funcionamiento

| Concepto | Descripción |
|---|---|
| **Periodo actual** | La hoja con la fecha más reciente |
| **Periodo de comparación** | La segunda hoja más reciente |
| **Histórico** | Todas las hojas disponibles |

No es necesario modificar el código al agregar nuevas hojas.

## Estructura del Proyecto

```
proyecto_mermas/
├── dataset.xlsx          # Datos fuente (Excel)
├── app.py                # Aplicación principal Streamlit
├── config.py             # Configuración centralizada
├── requirements.txt      # Dependencias
├── README.md
└── src/
    ├── __init__.py
    ├── data_loader.py    # Carga y detección de periodos
    ├── calculations.py   # Cálculos de indicadores
    ├── charts.py         # Gráficos Plotly
    ├── components.py     # Componentes UI y CSS
    └── utils.py          # Formato numérico
```

## Requisitos del Excel

Cada hoja debe contener:

- **Panel izquierdo** (columnas A-B): Resumen del periodo (PERIODO, INICIO, FIN, OPS CERRADAS, etc.)
- **Tabla de datos** (desde la columna de OP): OP, PRODUCTO, CLIENTE, FECHA DE CIERRE, CANTIDAD PLAN MT, CANTIDAD CIERRE MT, MERMA MT, % MERMA, % MERMA VS PERIODO
