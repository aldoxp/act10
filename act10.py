import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Smart Farming Analytics", page_icon="🌾", layout="wide")

st.title("🌾 Smart Farming - Análisis de Rendimiento de Cultivos 2024")

@st.cache_data
def load_data():
    df = pd.read_csv("Smart_Farming_Crop_Yield_2024.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()
st.success(f"✅ Datos cargados: {df.shape[0]} registros")

# Filtros (igual que antes)
st.sidebar.header("🔍 Filtros")
region = st.sidebar.selectbox("Región", ["Todas"] + sorted(df['region'].unique()))
crop = st.sidebar.selectbox("Cultivo", ["Todos"] + sorted(df['crop_type'].unique()))
yield_range = st.sidebar.slider(
    "Rendimiento (kg/ha)",
    float(df['yield_kg_per_hectare'].min()),
    float(df['yield_kg_per_hectare'].max()),
    (float(df['yield_kg_per_hectare'].min()), float(df['yield_kg_per_hectare'].max()))
)

df_filtered = df.copy()
if region != "Todas":
    df_filtered = df_filtered[df_filtered['region'] == region]
if crop != "Todos":
    df_filtered = df_filtered[df_filtered['crop_type'] == crop]
df_filtered = df_filtered[(df_filtered['yield_kg_per_hectare'] >= yield_range[0]) & 
                          (df_filtered['yield_kg_per_hectare'] <= yield_range[1])]

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rendimiento promedio", f"{df_filtered['yield_kg_per_hectare'].mean():.0f} kg/ha")
col2.metric("Rendimiento máximo", f"{df_filtered['yield_kg_per_hectare'].max():.0f} kg/ha")
col3.metric("Rendimiento mínimo", f"{df_filtered['yield_kg_per_hectare'].min():.0f} kg/ha")
col4.metric("Número de granjas", df_filtered['farm_id'].nunique())

with st.expander("📄 Ver datos filtrados"):
    st.dataframe(df_filtered, use_container_width=True)

st.header("📊 Análisis exploratorio")

# 1. Boxplot con Altair
st.subheader("Rendimiento por tipo de cultivo")
boxplot = alt.Chart(df_filtered).mark_boxplot().encode(
    x='crop_type',
    y='yield_kg_per_hectare',
    color='crop_type'
).properties(width=600)
st.altair_chart(boxplot, use_container_width=True)

# 2. Correlación (con gráfico de barras de Altair)
st.subheader("Correlación con rendimiento")
numeric_cols = ['soil_moisture_%', 'soil_pH', 'temperature_C', 'rainfall_mm', 
                'humidity_%', 'sunlight_hours', 'pesticide_usage_ml', 'total_days']
corr_values = [df_filtered[col].corr(df_filtered['yield_kg_per_hectare']) for col in numeric_cols]
corr_df = pd.DataFrame({'Variable': numeric_cols, 'Correlación': corr_values}).sort_values('Correlación', ascending=False)
corr_chart = alt.Chart(corr_df).mark_bar().encode(
    x='Variable',
    y='Correlación',
    color=alt.condition(alt.datum.Correlación > 0, alt.value("green"), alt.value("red"))
).properties(width=600)
st.altair_chart(corr_chart, use_container_width=True)

# 3. Scatter plot interactivo
st.subheader("Relación con rendimiento")
x_var = st.selectbox("Variable X", numeric_cols)
scatter = alt.Chart(df_filtered).mark_circle().encode(
    x=alt.X(x_var, title=x_var),
    y=alt.Y('yield_kg_per_hectare', title='Rendimiento (kg/ha)'),
    color='crop_type',
    tooltip=['farm_id', 'region', 'crop_type', 'yield_kg_per_hectare']
).properties(width=600, height=400).interactive()
st.altair_chart(scatter, use_container_width=True)

# 4. Mapa (con st.map si tienes lat/lon)
st.subheader("📍 Mapa de granjas")
if 'latitude' in df_filtered.columns and 'longitude' in df_filtered.columns:
    map_data = df_filtered[['latitude', 'longitude']].dropna()
    st.map(map_data)
else:
    st.info("No hay datos de ubicación")

# 5. Rendimiento por región (gráfico de barras simple)
st.subheader("Rendimiento promedio por región")
region_yield = df_filtered.groupby('region')['yield_kg_per_hectare'].mean().reset_index()
st.bar_chart(region_yield, x='region', y='yield_kg_per_hectare')

# Estadísticas
st.subheader("📈 Estadísticas descriptivas")
st.dataframe(df_filtered[numeric_cols + ['yield_kg_per_hectare']].describe(), use_container_width=True)

st.subheader("📌 Frecuencias")
col_cat1, col_cat2 = st.columns(2)
col_cat1.write("Cultivos más comunes")
col_cat1.dataframe(df_filtered['crop_type'].value_counts())
col_cat2.write("Estado de enfermedades")
col_cat2.dataframe(df_filtered['crop_disease_status'].value_counts())

st.markdown("---")
st.caption("App sin Plotly, usando Altair y gráficos nativos de Streamlit")
