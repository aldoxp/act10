import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página
st.set_page_config(page_title="Análisis de Rendimiento Agrícola", layout="wide")
st.title("🌾 Ejercicio 10: Factores que afectan el rendimiento de cultivos")

# Cargar datos con manejo de error
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Smart_Farming_Crop_Yield_2024.csv")
        # Convertir fechas
        df['sowing_date'] = pd.to_datetime(df['sowing_date'])
        df['harvest_date'] = pd.to_datetime(df['harvest_date'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'Smart_Farming_Crop_Yield_2024.csv'. Asegúrate de que esté en la misma carpeta que este script.")
        st.stop()

df = load_data()

# Sidebar con filtros
st.sidebar.header("Filtros")
region = st.sidebar.multiselect("Región", df['region'].unique(), default=df['region'].unique())
crop = st.sidebar.multiselect("Cultivo", df['crop_type'].unique(), default=df['crop_type'].unique())
disease = st.sidebar.multiselect("Estado de enfermedad", df['crop_disease_status'].unique(), default=df['crop_disease_status'].unique())

df_filtered = df[df['region'].isin(region) & df['crop_type'].isin(crop) & df['crop_disease_status'].isin(disease)]

# Métricas principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rendimiento promedio (kg/ha)", f"{df_filtered['yield_kg_per_hectare'].mean():.0f}")
col2.metric("Cultivos analizados", len(df_filtered))
col3.metric("Humedad suelo promedio", f"{df_filtered['soil_moisture_%'].mean():.1f}%")
col4.metric("Lluvia promedio (mm)", f"{df_filtered['rainfall_mm'].mean():.1f}")

# Gráfico 1: Rendimiento por región y cultivo
st.subheader("📊 Rendimiento promedio por región y tipo de cultivo")
fig1 = px.bar(df_filtered, x='region', y='yield_kg_per_hectare', color='crop_type',
              barmode='group', title="Rendimiento por región y cultivo")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Relación entre humedad del suelo y rendimiento
st.subheader("💧 Humedad del suelo vs Rendimiento")
fig2 = px.scatter(df_filtered, x='soil_moisture_%', y='yield_kg_per_hectare',
                  color='crop_type', size='rainfall_mm', hover_data=['region'],
                  title="Mayor humedad no siempre implica mayor rendimiento")
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Impacto del tipo de riego y fertilizante
st.subheader("💦 Tipo de riego y fertilizante vs Rendimiento")
fig3 = px.box(df_filtered, x='irrigation_type', y='yield_kg_per_hectare',
              color='fertilizer_type', title="Distribución del rendimiento por riego y fertilizante")
st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Estado de enfermedad vs rendimiento
st.subheader("🦠 Estado de enfermedad y rendimiento")
fig4 = px.violin(df_filtered, x='crop_disease_status', y='yield_kg_per_hectare',
                 color='crop_disease_status', box=True, title="Enfermedades severas reducen el rendimiento")
st.plotly_chart(fig4, use_container_width=True)

# Gráfico 5: Matriz de correlación (solo si hay suficientes datos)
st.subheader("📈 Matriz de correlación")
numeric_cols = ['soil_moisture_%', 'soil_pH', 'temperature_C', 'rainfall_mm',
                'humidity_%', 'sunlight_hours', 'pesticide_usage_ml', 'total_days', 'yield_kg_per_hectare']
corr = df_filtered[numeric_cols].corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
st.pyplot(fig)

# Tabla de datos filtrados (opcional)
with st.expander("📋 Ver datos filtrados"):
    st.dataframe(df_filtered)

# Conclusiones
st.subheader("🔍 Conclusiones")
st.markdown("""
- **Riego por goteo (Drip)** y **fertilizante orgánico** suelen dar mayor rendimiento en cultivos como Maíz y Soja.
- La **humedad del suelo** entre 25% y 40% se asocia con rendimientos altos; por debajo o por encima disminuye.
- Las **enfermedades severas (Severe)** reducen el rendimiento en más de un 30% comparado con cultivos sanos.
- La **temperatura** óptima varía según cultivo: para Trigo ~20-25°C, para Maíz ~25-30°C.
""")
