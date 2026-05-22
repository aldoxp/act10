import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Smart Farming Analytics", page_icon="🌾", layout="wide")

st.title("🌾 Smart Farming - Análisis de Rendimiento de Cultivos 2024")
st.markdown("Aplicación interactiva para explorar factores que afectan el rendimiento agrícola.")

# -------------------------------
# 1. Carga de datos con manejo de errores
# -------------------------------
@st.cache_data
def load_data():
    file_path = "Smart_Farming_Crop_Yield_2024.csv"
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='latin1')
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo '{file_path}'. Asegúrate de que esté en el mismo directorio.")
        st.stop()
    df.columns = df.columns.str.strip()
    return df

df = load_data()
st.success(f"✅ Datos cargados: {df.shape[0]} registros, {df.shape[1]} columnas")

# -------------------------------
# 2. Filtros en sidebar
# -------------------------------
st.sidebar.header("🔍 Filtros")
region = st.sidebar.selectbox("Región", ["Todas"] + sorted(df['region'].unique()))
crop = st.sidebar.selectbox("Cultivo", ["Todos"] + sorted(df['crop_type'].unique()))
yield_range = st.sidebar.slider(
    "Rendimiento (kg/ha)",
    float(df['yield_kg_per_hectare'].min()),
    float(df['yield_kg_per_hectare'].max()),
    (float(df['yield_kg_per_hectare'].min()), float(df['yield_kg_per_hectare'].max()))
)

# Aplicar filtros
df_filtered = df.copy()
if region != "Todas":
    df_filtered = df_filtered[df_filtered['region'] == region]
if crop != "Todos":
    df_filtered = df_filtered[df_filtered['crop_type'] == crop]
df_filtered = df_filtered[(df_filtered['yield_kg_per_hectare'] >= yield_range[0]) & 
                          (df_filtered['yield_kg_per_hectare'] <= yield_range[1])]

st.sidebar.markdown(f"**Registros mostrados:** {df_filtered.shape[0]}")

# -------------------------------
# 3. Métricas
# -------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rendimiento promedio", f"{df_filtered['yield_kg_per_hectare'].mean():.0f} kg/ha")
col2.metric("Rendimiento máximo", f"{df_filtered['yield_kg_per_hectare'].max():.0f} kg/ha")
col3.metric("Rendimiento mínimo", f"{df_filtered['yield_kg_per_hectare'].min():.0f} kg/ha")
col4.metric("Número de granjas", df_filtered['farm_id'].nunique())

# -------------------------------
# 4. Tabla de datos (expandible)
# -------------------------------
with st.expander("📄 Ver datos filtrados"):
    st.dataframe(df_filtered, use_container_width=True)

# -------------------------------
# 5. Visualizaciones
# -------------------------------
st.header("📊 Análisis exploratorio")

# Distribución del rendimiento por cultivo
st.subplot = st.subheader("Rendimiento por tipo de cultivo")
fig1 = px.box(df_filtered, x='crop_type', y='yield_kg_per_hectare', color='crop_type',
              title="Distribución del rendimiento por cultivo", points="all")
st.plotly_chart(fig1, use_container_width=True)

# Correlación con variables ambientales
st.subheader("Correlación entre variables ambientales y rendimiento")
numeric_cols = ['soil_moisture_%', 'soil_pH', 'temperature_C', 'rainfall_mm', 
                'humidity_%', 'sunlight_hours', 'pesticide_usage_ml', 'total_days', 
                'yield_kg_per_hectare']
corr = df_filtered[numeric_cols].corr()['yield_kg_per_hectare'].sort_values(ascending=False)
fig_corr = px.bar(x=corr.index[1:], y=corr.values[1:], 
                  labels={'x':'Variable', 'y':'Correlación con rendimiento'},
                  title="Importancia de cada variable en el rendimiento")
st.plotly_chart(fig_corr, use_container_width=True)

# Relación entre dos variables (interactivo)
st.subheader("Relación entre variable ambiental y rendimiento")
x_var = st.selectbox("Selecciona variable X", numeric_cols[:-1], index=0)
fig2 = px.scatter(df_filtered, x=x_var, y='yield_kg_per_hectare', color='crop_type',
                  size='total_days', hover_data=['farm_id', 'region'],
                  title=f"{x_var} vs Rendimiento")
st.plotly_chart(fig2, use_container_width=True)

# Mapa de ubicaciones
st.subheader("📍 Ubicación geográfica de las granjas")
if 'latitude' in df_filtered.columns and 'longitude' in df_filtered.columns:
    df_map = df_filtered.dropna(subset=['latitude', 'longitude'])
    fig_map = px.scatter_mapbox(df_map, lat='latitude', lon='longitude', 
                                color='yield_kg_per_hectare', size='yield_kg_per_hectare',
                                hover_name='farm_id', hover_data=['crop_type', 'region'],
                                color_continuous_scale='Viridis',
                                title="Rendimiento por ubicación")
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("No se encontraron columnas de latitud/longitud para el mapa.")

# Rendimiento por región
st.subheader("Rendimiento promedio por región")
region_yield = df_filtered.groupby('region')['yield_kg_per_hectare'].mean().reset_index()
fig3 = px.bar(region_yield, x='region', y='yield_kg_per_hectare', color='region',
              title="Rendimiento medio por región")
st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# 6. Estadísticas
# -------------------------------
st.subheader("📈 Estadísticas descriptivas")
st.dataframe(df_filtered[numeric_cols].describe(), use_container_width=True)

st.subheader("📌 Frecuencia de cultivos y enfermedades")
col_cat1, col_cat2 = st.columns(2)
col_cat1.write("**Cultivos más comunes**")
col_cat1.dataframe(df_filtered['crop_type'].value_counts().reset_index().rename(
    columns={'index': 'Cultivo', 'crop_type': 'Conteo'}))
col_cat2.write("**Estado de enfermedades**")
col_cat2.dataframe(df_filtered['crop_disease_status'].value_counts().reset_index().rename(
    columns={'index': 'Estado', 'crop_disease_status': 'Conteo'}))

st.markdown("---")
st.caption("Desarrollado con Streamlit | Datos Smart Farming Crop Yield 2024")
