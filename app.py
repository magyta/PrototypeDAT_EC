"""
Dashboard — Control Metabólico DM2
Formularios 4, 5, 7 y 7.1 — Zona de Salud 3
Programa de Enfermedades Crónicas — MSP Ecuador

Uso:
    python dashboard_dm2.py
    Abrir navegador en http://127.0.0.1:8050
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os

# ══════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN DE LA PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Dashboard DM2 — Control Metabólico",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores institucionales
C = {
    "azul":    "#2E5D9E",
    "teal":    "#0F6E56",
    "morado":  "#534AB7",
    "ambar":   "#C97A0B",
    "coral":   "#C2401F",
    "gris":    "#64748b",
    "verde":   "#16A34A",
    "rojo":    "#DC2626",
}

# ══════════════════════════════════════════════════════════════════
# 2. CARGA Y PREPARACIÓN DE DATOS (Con caché para optimizar rendimiento)
# ══════════════════════════════════════════════════════════════════
@st.cache_data
def cargar_datos():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else "."
    CSV_PATH = os.path.join(BASE_DIR, "datos_control_metabolico.csv")
    
    if not os.path.exists(CSV_PATH):
        st.error(f"❌ No se encontró el archivo CSV en la ruta: {os.path.abspath(CSV_PATH)}")
        st.stop()
        
    df = pd.read_csv(CSV_PATH)
    
    # Homologación estricta de columnas booleanas
    bool_cols = ["hta", "dislipidemia", "obesidad", "prescripcion_educativa",
                 "actividad_fisica_prescrita", "cambio_tratamiento",
                 "hospitalizacion_periodo", "derivacion_especialidad",
                 "ctrl_hba1c", "ctrl_presion_arterial", "ctrl_ldl", "triple_control_abc"]
    
    for c in bool_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip().str.upper().map(
                {"TRUE": True, "FALSE": False, "1": True, "0": False, "NAN": False}
            ).fillna(False)
            
    return df

df_raw = cargar_datos()

# ══════════════════════════════════════════════════════════════════
# 3. BARRA LATERAL (FILTROS)
# ══════════════════════════════════════════════════════════════════
st.sidebar.header("Filtros de Búsqueda")
unidades_disponibles = ["TODAS"] + sorted(df_raw["unidad_operativa"].dropna().unique().tolist())
unidad_seleccionada = st.sidebar.selectbox("Seleccione Unidad Operativa:", unidades_disponibles)

# Filtrado del dataframe
if unidad_seleccionada == "TODAS":
    df = df_raw
else:
    df = df_raw[df_raw["unidad_operativa"] == unidad_seleccionada]

# Verificar que existan datos
if df.empty:
    st.warning("⚠️ No hay datos disponibles para la unidad seleccionada.")
    st.stop()

# ══════════════════════════════════════════════════════════════════
# 4. ENCABEZADO PRINCIPAL
# ══════════════════════════════════════════════════════════════════
st.title("🩺 Dashboard — Control Metabólico DM2")
st.markdown("### Programa de Enfermedades Crónicas — Zona de Salud 3")
st.write(f"Visualizando datos de: **{unidad_seleccionada}** ({len(df)} pacientes registrados)")
st.divider()
# Función auxiliar para porcentajes
def pct(series_bool):
    if len(series_bool) == 0:
        return 0.0
    return round(float(series_bool.sum()) / len(series_bool) * 100, 1)

# ══════════════════════════════════════════════════════════════════
# 5. BLOQUE DE TARJETAS KPI (Métricas Clave)
# ══════════════════════════════════════════════════════════════════
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    st.metric(label="HbA1c < 7%", value=f"{pct(df['ctrl_hba1c'])}%")
with kpi2:
    st.metric(label="PA < 130/80", value=f"{pct(df['ctrl_presion_arterial'])}%")
with kpi3:
    st.metric(label="LDL < 100", value=f"{pct(df['ctrl_ldl'])}%")
with kpi4:
    st.metric(label="Control ABC", value=f"{pct(df['triple_control_abc'])}%")
with kpi5:
    st.metric(label="Educación", value=f"{pct(df['prescripcion_educativa'])}%")
with kpi6:
    red_mean = round(float(df["reduccion_hba1c"].mean()), 2)
    st.metric(label="Reduc. Media", value=f"{red_mean} pts")

st.markdown("<br>", unsafe_allow_html=True)

# Configuración base para gráficos de Plotly en Streamlit
layout_comun = dict(
    font_family="Segoe UI, Arial, sans-serif",
    margin=dict(l=40, r=20, t=40, b=40),
    height=300,
)

# Fila de Prescripción Educativa y Actividad Física

# Si llegas a usar la de actividad física en algún gráfico, recuerda llamarla así:
# total_af = df["actividad_fisica_prescrita"].sum()

# ══════════════════════════════════════════════════════════════════
# 6. FILA 1 DE GRÁFICOS: Gauges e Indicadores y Reducción por Unidad
# ══════════════════════════════════════════════════════════════════
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### Gauges de Control Métrico")
    fig_gauges = go.Figure()
    metrics = [
        (pct(df['ctrl_hba1c']), "HbA1c", C["azul"]),
        (pct(df['ctrl_presion_arterial']), "P.A.", C["teal"]),
        (pct(df['ctrl_ldl']), "LDL", C["morado"]),
        (pct(df['triple_control_abc']), "ABC", C["coral"])
    ]
    for i, (val, lab, col) in enumerate(metrics):
        fig_gauges.add_trace(go.Indicator(
            mode="gauge+number", value=val,
            title={"text": lab, "font": {"size": 12}},
            number={"suffix": "%", "font": {"size": 16}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": col}},
            domain={"row": 0, "column": i}
        ))
    fig_gauges.update_layout(grid={"rows": 1, "columns": 4, "pattern": "independent"}, margin=dict(l=10, r=10, t=10, b=10), height=200)
    st.plotly_chart(fig_gauges, use_container_width=True)

with col_g2:
    st.markdown("#### Reducción Media de HbA1c por Unidad Operativa")
    r_uo = df.groupby("unidad_operativa")["reduccion_hba1c"].mean().round(2).reset_index()
    fig_bar_red = go.Figure(go.Bar(y=r_uo["unidad_operativa"], x=r_uo["reduccion_hba1c"], orientation="h", marker_color=C["azul"]))
    fig_bar_red.update_layout(**layout_comun, xaxis_title="Puntos de reducción")
    st.plotly_chart(fig_bar_red, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# 7. FILA 2 DE GRÁFICOS: Distribución de HbA1c y Presión Arterial (Boxplot)
# ══════════════════════════════════════════════════════════════════
col_g3, col_g4 = st.columns(2)

with col_g3:
    st.markdown("#### Distribución de HbA1c (Basal vs 6 Meses)")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=df["hba1c_basal"], name="Basal", marker_color=C["coral"], opacity=0.7))
    fig_hist.add_trace(go.Histogram(x=df["hba1c_6m"], name="6 Meses", marker_color=C["azul"], opacity=0.7))
    fig_hist.update_layout(**layout_comun, barmode="overlay", yaxis_title="Número de Pacientes", xaxis_title="Porcentaje HbA1c")
    st.plotly_chart(fig_hist, use_container_width=True)

with col_g4:
    st.markdown("#### Presión Arterial Sistólica (PAS)")
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(y=df["pas_basal"], name="PAS Basal", marker_color=C["coral"]))
    fig_box.add_trace(go.Box(y=df["pas_6m"], name="PAS 6 Meses", marker_color=C["azul"]))
    fig_box.update_layout(**layout_comun, yaxis_title="PAS (mmHg)")
    st.plotly_chart(fig_box, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# 8. FILA 3 DE GRÁFICOS: Evolución y Adherencia Educativa
# ══════════════════════════════════════════════════════════════════
col_g5, col_g6 = st.columns([1.2, 0.8])

with col_g5:
    st.markdown("#### Evolución HbA1c Individual y Triple Control")
    df["triple_str"] = df["triple_control_abc"].map({True: "Control Óptimo (ABC)", False: "Fuera de Rango"})
    fig_scatter = px.scatter(
        df, x="hba1c_basal", y="hba1c_6m", color="triple_str",
        color_discrete_map={"Control Óptimo (ABC)": C["teal"], "Fuera de Rango": C["coral"]},
        labels={"hba1c_basal": "HbA1c Basal", "hba1c_6m": "HbA1c 6 Meses", "triple_str": "Estado"}
    )
    fig_scatter.update_layout(**layout_comun)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_g6:
    st.markdown("#### Prescripción Educativa")
    total_educados = df["prescripcion_educativa"].sum()

    total_no = len(df) - total_educados
    fig_pie = go.Figure(go.Pie(labels=["Recibió Educación", "No Recibió"], values=[total_educados, total_no], hole=0.5, marker_colors=[C["ambar"], "#E2E8F0"]))
    fig_pie.update_layout(**layout_comun, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# 9. FILA 4 DE GRÁFICOS: Adherencia Farmacológica y Tiempos de Dx
# ══════════════════════════════════════════════════════════════════
col_g7, col_g8 = st.columns(2)

with col_g7:
    st.markdown("#### Niveles de Adherencia Farmacológica")
    ord_adh = ["Alta", "Media", "Baja"]
    adh_f = df["adherencia_farmacologica"].value_counts().reindex(ord_adh, fill_value=0)
    fig_adh = go.Figure(go.Bar(x=ord_adh, y=adh_f.values, marker_color=C["teal"]))
    fig_adh.update_layout(**layout_comun, yaxis_title="Pacientes", xaxis_title="Nivel de Adherencia")
    st.plotly_chart(fig_adh, use_container_width=True)

with col_g8:
    st.markdown("#### Distribución del Tiempo Dx a Tratamiento")
    fig_hist_tto = go.Figure(go.Histogram(x=df["dias_dx_a_tratamiento"], marker_color=C["morado"]))
    fig_hist_tto.update_layout(**layout_comun, xaxis_title="Días transcurridos", yaxis_title="Pacientes")
    st.plotly_chart(fig_hist_tto, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# 10. TABLA RESUMEN OPERATIVO FINAL
# ══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("#### 📋 Tabla Resumen Operativo por Unidad")

resumen = df.groupby("unidad_operativa").agg(
    Pacientes=("id_paciente", "count"),
    HbA1c_Basal_Media=("hba1c_basal", lambda x: round(x.mean(), 2)),
    HbA1c_6M_Media=("hba1c_6m", lambda x: round(x.mean(), 2)),
    Reduccion_Media=("reduccion_hba1c", lambda x: round(x.mean(), 2))
).reset_index()

st.dataframe(resumen, use_container_width=True, hide_index=True)