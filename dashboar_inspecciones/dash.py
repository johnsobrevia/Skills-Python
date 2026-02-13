import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy.interpolate import make_interp_spline

# 1. Configuración de página
st.set_page_config(page_title="Dashboard de Mantenimiento Predictivo", layout="wide")

import os

# 2. Carga y Limpieza de Datos
@st.cache_data
def cargar_datos():
    # Obtener la ruta del directorio del script actual
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'DF_Clean.csv')
    
    df = pd.read_csv(csv_path)
    df['FECHA_INSPECCION'] = pd.to_datetime(df['FECHA_INSPECCION'], dayfirst=True)
    df = df[df['DESCRIPCION_COMPONENTE'] != 'POLÍN DE CARGA']
    return df

df = cargar_datos()

# 3. Sidebar - Filtros
st.sidebar.header("Filtros de Análisis")
ruta_sel = st.sidebar.selectbox("Ruta", sorted(df['RUTA_INSP'].unique()))
equipos = sorted(df[df['RUTA_INSP'] == ruta_sel]['TAG_EQUIPO'].unique())
tag_sel = st.sidebar.selectbox("Tag Equipo", equipos)
componentes = sorted(df[df['TAG_EQUIPO'] == tag_sel]['DESCRIPCION_COMPONENTE'].unique())
comp_sel = st.sidebar.selectbox("Componente", componentes)

# Solo mostrar filtro de Lado Polín si el componente no es un REDUCTOR
if "REDUCTOR" in comp_sel.upper():
    lado_sel = "Todos"
else:
    lados_unique = df[(df['TAG_EQUIPO'] == tag_sel) & (df['DESCRIPCION_COMPONENTE'] == comp_sel)]['LADO_POLIN'].dropna().unique().tolist()
    lados = ["Todos"] + sorted([str(l) for l in lados_unique])
    lado_sel = st.sidebar.selectbox("Lado Polín", lados)

rango = st.sidebar.date_input("Rango de Fechas", [df['FECHA_INSPECCION'].min(), df['FECHA_INSPECCION'].max()])


# 4. Procesamiento
if len(rango) == 2:
    inicio, fin = pd.to_datetime(rango[0]), pd.to_datetime(rango[1])
    mask = (df['TAG_EQUIPO'] == tag_sel) & (df['DESCRIPCION_COMPONENTE'] == comp_sel) & \
           (df['FECHA_INSPECCION'] >= inicio) & (df['FECHA_INSPECCION'] <= fin)
    
    if lado_sel != "Todos":
        mask = mask & (df['LADO_POLIN'] == lado_sel)
    df_f = df[mask].copy()
    df_plot = df_f.groupby('FECHA_INSPECCION')['TEMP_F1'].mean().reset_index().sort_values('FECHA_INSPECCION')

    st.title(f"Análisis de Tendencia: {comp_sel}")
    

    if not df_plot.empty:
        # KPIs
        avg_t, max_t = df_plot['TEMP_F1'].mean(), df_plot['TEMP_F1'].max()
        k1, k2, k3 = st.columns(3)
        k1.metric("Promedio", f"{avg_t:.1f} °C")
        k2.metric("Máximo", f"{max_t:.1f} °C")
        k3.metric("N° Inspecciones", len(df_plot))

        # 5. CÁLCULO DE TENDENCIA Y SUAVIZADO
        x_num = np.array(range(len(df_plot)))
        y_vals = df_plot['TEMP_F1'].values

        # A. Línea de tendencia (Regresión Lineal)
        z = np.polyfit(x_num, y_vals, 1) # Calcula la pendiente y la intersección
        p = np.poly1d(z)
        y_trend = p(x_num)

        # B. Suavizado (Spline) - solo si hay suficientes puntos
        fig = go.Figure()

        if len(df_plot) >= 3:
            x_smooth = np.linspace(x_num.min(), x_num.max(), 300)
            y_smooth = make_interp_spline(x_num, y_vals, k=3)(x_smooth)
            fechas_smooth = pd.to_datetime(np.interp(x_smooth, x_num, df_plot['FECHA_INSPECCION'].astype(np.int64)))
            
            # Línea Suavizada
            fig.add_trace(go.Scatter(x=fechas_smooth, y=y_smooth, name='Curva de Evolución',
                                     line=dict(color='#00D4FF', width=2), hoverinfo='skip'))

        # C. Línea de Tendencia Lineal (Punteada)
        fig.add_trace(go.Scatter(
            x=df_plot['FECHA_INSPECCION'], y=y_trend,
            name='Tendencia Lineal',
            line=dict(color='#e031a9', width=2, dash='solid'),
            opacity=0.6
        ))

        # D. Puntos Reales
        fig.add_trace(go.Scatter(
            x=df_plot['FECHA_INSPECCION'], y=y_vals,
            mode='markers', name='Mediciones',
            marker=dict(color='white', size=8, line=dict(color='#00D4FF', width=1)),
            hovertemplate='<b>Fecha:</b> %{x|%d %b %Y}<br><b>Temp:</b> %{y:.1f}°C<extra></extra>'
        ))

        # Configuración Visual
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 90], title="Temperatura °C", gridcolor='#333333'),
            xaxis=dict(title="Fecha de Inspección", gridcolor='#333333', tickformat='%d %b %Y', tickangle=-45),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabla de datos para auditoría
        with st.expander("Ver detalle de mediciones"):
            df_f['FECHA_INSPECCION'] = df_f['FECHA_INSPECCION'].dt.date
            st.dataframe(df_f[['FECHA_INSPECCION', 'LADO_POLIN', 'TEMP_F1', 'DESCRIPCION_COMPONENTE']].sort_values('FECHA_INSPECCION', ascending=False))
    else:
        st.warning("No hay datos para los filtros seleccionados.")