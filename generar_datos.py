"""
Generador de datos sintéticos — Control Metabólico DM2
Formularios: 4 (Evaluación Inicial GPC), 5 (Prescripción Educativa),
             7 (Evaluación Subsecuente GPC), 7.1 (Evolución del caso)
Zona de Salud 3 — Programa de Enfermedades Crónicas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 320  # número de pacientes

# ─── Catálogos ────────────────────────────────────────────────────
UNIDADES = [
    "CS Riobamba Norte", "CS Riobamba Sur", "CS Chambo",
    "CS Guano", "CS Penipe", "CS Alausí", "CS Chunchi", "CS Colta"
]
ETNIAS    = ["Mestizo", "Indígena", "Blanco", "Afroecuatoriano"]
SEXOS     = ["Masculino", "Femenino"]
NIVELES_EDUCACION = ["Ninguno", "Primaria", "Secundaria", "Superior"]
PRESCRIPTORES = [f"Dr./Dra. {n}" for n in [
    "Guamán", "Pilco", "Ramos", "Lema", "Torres", "Álvarez", "Cando", "Naula"
]]
TIPO_DM   = ["DM2 Sin complicaciones", "DM2 Con complicaciones"]
ACTIVIDAD_FISICA = ["Sedentario", "Leve", "Moderada", "Intensa"]
ADHERENCIA_LABELS = ["Alta", "Media", "Baja"]

# ─── Form. 4 — Evaluación Inicial ────────────────────────────────
ids = [f"PAC-{str(i+1).zfill(4)}" for i in range(N)]
fechas_captacion = [
    datetime(2023, 1, 1) + timedelta(days=random.randint(0, 540))
    for _ in range(N)
]
edades   = np.random.randint(35, 80, N)
sexos    = np.random.choice(SEXOS, N, p=[0.42, 0.58])
etnias   = np.random.choice(ETNIAS, N, p=[0.48, 0.44, 0.06, 0.02])
educacion= np.random.choice(NIVELES_EDUCACION, N, p=[0.12, 0.38, 0.34, 0.16])
unidades = np.random.choice(UNIDADES, N)

# Peso, talla, IMC
tallas   = np.round(np.random.normal(1.58, 0.07, N), 2)
pesos    = np.round(np.random.normal(78, 14, N), 1)
imc      = np.round(pesos / (tallas ** 2), 1)

# HbA1c basal (Form 4) — distribución realista: mayoría mal controlada al inicio
hba1c_basal = np.round(np.random.normal(8.9, 1.8, N).clip(5.5, 14.0), 1)

# Glucemia en ayunas basal
glucemia_basal = np.round(hba1c_basal * 28.7 - 46.7 + np.random.normal(0, 18, N), 0).clip(80, 450)

# Presión arterial basal
pas_basal = np.round(np.random.normal(142, 18, N), 0).clip(100, 200)
pad_basal = np.round(np.random.normal(88, 10, N), 0).clip(60, 120)

# LDL basal
ldl_basal = np.round(np.random.normal(128, 32, N), 0).clip(50, 260)

# Colesterol total, triglicéridos
col_total = np.round(ldl_basal + np.random.normal(48, 12, N), 0).clip(100, 350)
triglice  = np.round(np.random.normal(210, 65, N), 0).clip(60, 500)

# Tipo DM, años evolución, comorbilidades
tipo_dm   = np.random.choice(TIPO_DM, N, p=[0.62, 0.38])
anios_dm  = np.random.randint(0, 20, N)
hta       = np.random.choice([True, False], N, p=[0.68, 0.32])
dislip    = np.random.choice([True, False], N, p=[0.55, 0.45])
obesidad  = (imc >= 30)

# ─── Form. 5 — Prescripción Educativa ────────────────────────────
prescripcion_educativa = np.random.choice([True, False], N, p=[0.63, 0.37])
temas_educacion = np.where(
    prescripcion_educativa,
    np.random.choice(
        ["Alimentación saludable", "Actividad física", "Monitoreo glucémico",
         "Adherencia farmacológica", "Cuidado de pies", "Autogestión integral"],
        N
    ), "No aplicada"
)
actividad_fisica_prescrita = np.random.choice([True, False], N, p=[0.55, 0.45])
nivel_af = np.where(
    actividad_fisica_prescrita,
    np.random.choice(ACTIVIDAD_FISICA[1:], N),
    "Sedentario"
)

# ─── Form. 7 — Evaluación Subsecuente (seguimiento a 6 meses) ────
# Simulamos que el tratamiento produce mejora parcial
mejora_hba1c = np.random.normal(1.2, 0.8, N).clip(-0.5, 4.5)
hba1c_6m = np.round((hba1c_basal - mejora_hba1c).clip(5.0, 13.0), 1)

mejora_pas = np.random.normal(10, 8, N).clip(-5, 30)
pas_6m = np.round((pas_basal - mejora_pas).clip(95, 195), 0)
pad_6m = np.round((pad_basal - np.random.normal(5, 4, N)).clip(58, 115), 0)

mejora_ldl = np.random.normal(18, 12, N).clip(-5, 55)
ldl_6m = np.round((ldl_basal - mejora_ldl).clip(45, 250), 0)

glucemia_6m = np.round(hba1c_6m * 28.7 - 46.7 + np.random.normal(0, 15, N), 0).clip(75, 400)

peso_6m = np.round(pesos - np.random.normal(1.8, 2.5, N), 1)
imc_6m  = np.round(peso_6m / (tallas ** 2), 1)

n_consultas = np.random.randint(1, 5, N)
adherencia_consultas = np.random.choice(ADHERENCIA_LABELS, N, p=[0.38, 0.37, 0.25])
prescriptor = np.random.choice(PRESCRIPTORES, N)

# ─── Form. 7.1 — Evolución del caso / notas rápidas ──────────────
fecha_ult_control = [
    fc + timedelta(days=random.randint(150, 210))
    for fc in fechas_captacion
]
cambio_tto = np.random.choice([True, False], N, p=[0.44, 0.56])
hospitalizacion_periodo = np.random.choice([True, False], N, p=[0.09, 0.91])
derivacion_especialidad = np.random.choice([True, False], N, p=[0.28, 0.72])
adherencia_farmaco = np.random.choice(ADHERENCIA_LABELS, N, p=[0.40, 0.35, 0.25])

# ─── Indicadores calculados ───────────────────────────────────────
ctrl_hba1c      = hba1c_6m < 7.0
ctrl_pas        = pas_6m < 130
ctrl_pad        = pad_6m < 80
ctrl_pa         = ctrl_pas & ctrl_pad
ctrl_ldl        = ldl_6m < 100
triple_control  = ctrl_hba1c & ctrl_pa & ctrl_ldl
reduccion_hba1c = np.round(hba1c_basal - hba1c_6m, 1)
tiempo_dx_tto   = np.random.randint(3, 45, N)

# ─── Ensamblado del DataFrame ─────────────────────────────────────
df = pd.DataFrame({
    # Identificación
    "id_paciente":           ids,
    "unidad_operativa":      unidades,
    "fecha_captacion":       fechas_captacion,
    "fecha_ult_control":     fecha_ult_control,
    # Sociodemográfico
    "edad":                  edades,
    "sexo":                  sexos,
    "etnia":                 etnias,
    "nivel_educacion":       educacion,
    "anios_evolucion_dm":    anios_dm,
    "tipo_dm":               tipo_dm,
    # Antropometría
    "talla_m":               tallas,
    "peso_kg_basal":         pesos,
    "imc_basal":             imc,
    "peso_kg_6m":            peso_6m,
    "imc_6m":                imc_6m,
    # Comorbilidades
    "hta":                   hta,
    "dislipidemia":          dislip,
    "obesidad":              obesidad,
    # Form. 4 — Evaluación Inicial
    "hba1c_basal":           hba1c_basal,
    "glucemia_ayunas_basal": glucemia_basal,
    "pas_basal":             pas_basal,
    "pad_basal":             pad_basal,
    "ldl_basal":             ldl_basal,
    "col_total_basal":       col_total,
    "trigliceridos_basal":   triglice,
    # Form. 5 — Prescripción Educativa
    "prescripcion_educativa":       prescripcion_educativa,
    "tema_educacion":               temas_educacion,
    "actividad_fisica_prescrita":   actividad_fisica_prescrita,
    "nivel_actividad_fisica":       nivel_af,
    # Form. 7 — Evaluación Subsecuente
    "hba1c_6m":              hba1c_6m,
    "glucemia_ayunas_6m":    glucemia_6m,
    "pas_6m":                pas_6m,
    "pad_6m":                pad_6m,
    "ldl_6m":                ldl_6m,
    "n_consultas_realizadas":n_consultas,
    "adherencia_consultas":  adherencia_consultas,
    "prescriptor":           prescriptor,
    # Form. 7.1 — Evolución del caso
    "cambio_tratamiento":         cambio_tto,
    "hospitalizacion_periodo":    hospitalizacion_periodo,
    "derivacion_especialidad":    derivacion_especialidad,
    "adherencia_farmacologica":   adherencia_farmaco,
    "dias_dx_a_tratamiento":      tiempo_dx_tto,
    # Indicadores calculados
    "ctrl_hba1c":            ctrl_hba1c,
    "ctrl_presion_arterial": ctrl_pa,
    "ctrl_ldl":              ctrl_ldl,
    "triple_control_abc":    triple_control,
    "reduccion_hba1c":       reduccion_hba1c,
})

df.to_csv("/home/claude/datos_control_metabolico.csv", index=False)
print(f"✓ Dataset generado: {len(df)} pacientes, {len(df.columns)} variables")
print(df.dtypes.to_string())
print("\nPreview:")
print(df[["id_paciente","unidad_operativa","hba1c_basal","hba1c_6m",
          "ctrl_hba1c","triple_control_abc","reduccion_hba1c"]].head(8).to_string(index=False))
