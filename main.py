"""
🌾 Dashboard Interactivo: Producción de Cereales en Colombia
Análisis Exploratorio de Datos - Grupo 2 MAD
Fecha de creación: 24 de febrero de 2026
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ==================== CONFIGURACIÓN DE LA PÁGINA ====================
st.set_page_config(
    page_title="Dashboard Cereales Colombia",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTILOS CSS ====================
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #E8F5E9, #C8E6C9);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F1F8E9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #558B2F;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1976D2;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== CARGA DE DATOS ====================
@st.cache_data
def load_data():
    """Carga y preprocesa los datos de cereales desde Dropbox"""
    url = 'https://www.dropbox.com/scl/fi/e3iwe3z3jszouxues5bai/data21022026.csv?rlkey=fb1ex5sbf7yz4p0im8gfiziwm&st=va67mghf&dl=1'
    
    # Cargar dataset completo
    df_completo = pd.read_csv(url, delimiter=';', encoding='utf-8')
    
    # Limpiar nombres de columnas
    df_completo.columns = df_completo.columns.str.strip().str.replace('\n', ' ')
    
    # Filtrar solo CEREALES
    df = df_completo[df_completo['GRUPO  DE CULTIVO'].str.strip().str.upper() == 'CEREALES'].copy()
    
    # Renombrar columnas
    column_mapping = {
        'CÓD.  DEP.': 'cod_dep',
        'DEPARTAMENTO': 'departamento',
        'CÓD. MUN.': 'cod_mun',
        'MUNICIPIO': 'municipio',
        'GRUPO  DE CULTIVO': 'grupo_cultivo',
        'SUBGRUPO  DE CULTIVO': 'subgrupo_cultivo',
        'CULTIVO': 'cultivo',
        'DESAGREGACIÓN REGIONAL Y/O SISTEMA PRODUCTIVO': 'sistema_productivo',
        'AÑO': 'año',
        'PERIODO': 'periodo',
        'Área Sembrada (ha)': 'area_sembrada',
        'Área Cosechada (ha)': 'area_cosechada',
        'Producción (t)': 'produccion',
        'Rendimiento (t/ha)': 'rendimiento',
        'ESTADO FISICO PRODUCCION': 'estado_fisico',
        'NOMBRE  CIENTIFICO': 'nombre_cientifico',
        'CICLO DE CULTIVO': 'ciclo_cultivo'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    
    # Convertir columnas numéricas
    numeric_columns = ['area_sembrada', 'area_cosechada', 'produccion', 'rendimiento']
    for col in numeric_columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '.').astype(float)
    
    return df

# Cargar datos
with st.spinner('Cargando datos de cereales...'):
    df = load_data()

# ==================== SIDEBAR - INFORMACIÓN ====================
st.sidebar.markdown("## Información del Dashboard")
st.sidebar.markdown("---")
st.sidebar.info("""
Este dashboard muestra la totalidad de los datos de producción de cereales en Colombia.

Todos los cereales, departamentos y años disponibles están incluidos en las visualizaciones.
""")

# ==================== DATOS COMPLETOS (SIN FILTROS) ====================
# Mostrar todos los datos sin aplicar filtros
df_filtrado = df.copy()

# ==================== HEADER ====================
st.markdown('<div class="main-header">Dashboard: Producción de Cereales en Colombia</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h3>Contexto del Dashboard</h3>
    <p><strong>Objetivo:</strong> Analizar la producción de cereales en Colombia mediante datos de las 
    Evaluaciones Agropecuarias Municipales (EVA) del Ministerio de Agricultura.</p>
    <p><strong>Preguntas Analíticas:</strong></p>
    <ul>
        <li>¿Cuál es la distribución geográfica de la producción de cereales?</li>
        <li>¿Qué cereales tienen mayor rendimiento y producción?</li>
        <li>¿Cómo ha evolucionado la producción a lo largo del tiempo?</li>
        <li>¿Existen diferencias entre sistemas productivos?</li>
    </ul>
    <p><strong>Instrucciones:</strong> Utiliza los filtros en la barra lateral izquierda para personalizar 
    las visualizaciones según tus necesidades de análisis.</p>
</div>
""", unsafe_allow_html=True)

# ==================== MÉTRICAS PRINCIPALES ====================
st.markdown("## Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_produccion = df_filtrado['produccion'].sum() / 1_000_000  # Millones de toneladas
    st.metric(
        label="Producción Total",
        value=f"{total_produccion:.2f} M ton",
        help="Producción total de cereales en millones de toneladas"
    )

with col2:
    area_total = df_filtrado['area_sembrada'].sum() / 1_000  # Miles de hectáreas
    st.metric(
        label="Área Sembrada",
        value=f"{area_total:.1f}K ha",
        help="Área total sembrada en miles de hectáreas"
    )

with col3:
    rendimiento_promedio = df_filtrado['rendimiento'].mean()
    st.metric(
        label="Rendimiento Promedio",
        value=f"{rendimiento_promedio:.2f} t/ha",
        help="Rendimiento promedio en toneladas por hectárea"
    )

with col4:
    num_municipios = df_filtrado['municipio'].nunique()
    st.metric(
        label="Municipios",
        value=f"{num_municipios}",
        help="Número de municipios productores"
    )

st.markdown("---")

# ==================== VISUALIZACIÓN 1: DISTRIBUCIÓN GEOGRÁFICA ====================
st.markdown("## Visualización 1: Distribución Geográfica de la Producción")

col1, col2 = st.columns([2, 1])

with col1:
    # Producción por departamento - Ranking completo
    produccion_dep = df_filtrado.groupby('departamento')['produccion'].sum().sort_values(ascending=False)
    
    fig1 = px.bar(
        x=produccion_dep.values / 1000,
        y=produccion_dep.index,
        orientation='h',
        title='Ranking Completo de Departamentos por Producción de Cereales',
        labels={'x': 'Producción (miles de toneladas)', 'y': 'Departamento'},
        color=produccion_dep.values,
        color_continuous_scale='Greens'
    )
    fig1.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Interpretación")
    st.markdown(f"""
    - **Departamentos analizados:** {df_filtrado['departamento'].nunique()}
    - **Líder en producción:** {produccion_dep.index[0]}
    - **Producción líder:** {produccion_dep.values[0]/1000:.1f}K ton
    - **Concentración:** Los top 5 representan el {(produccion_dep.head(5).sum() / produccion_dep.sum() * 100):.1f}% del total
    
    Esta visualización muestra el ranking completo de departamentos productores de cereales en Colombia.
    """)

st.markdown("---")

# ==================== VISUALIZACIÓN 2: COMPARACIÓN DE CEREALES ====================
st.markdown("## Visualización 2: Comparación entre Tipos de Cereales")

col1, col2 = st.columns(2)

with col1:
    # Producción por tipo de cereal (ordenado de mayor a menor)
    produccion_cereal = df_filtrado.groupby('cultivo')['produccion'].sum().sort_values(ascending=False)
    
    fig2 = go.Figure(data=[go.Pie(
        labels=produccion_cereal.index,
        values=produccion_cereal.values,
        hole=0.4,
        marker=dict(colors=px.colors.sequential.Greens)
    )])
    fig2.update_layout(
        title='Distribución de Producción por Tipo de Cereal',
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    # Rendimiento por tipo de cereal
    rendimiento_cereal = df_filtrado.groupby('cultivo')['rendimiento'].mean().sort_values(ascending=False)
    
    fig3 = px.bar(
        x=rendimiento_cereal.index,
        y=rendimiento_cereal.values,
        title='Rendimiento Promedio por Tipo de Cereal',
        labels={'x': 'Cereal', 'y': 'Rendimiento (t/ha)'},
        color=rendimiento_cereal.values,
        color_continuous_scale='Oranges'
    )
    fig3.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("### Análisis Comparativo")
st.markdown(f"""
- **Cereal más producido:** {produccion_cereal.index[0]} ({produccion_cereal.values[0]/1000:.1f}K ton)
- **Mayor rendimiento:** {rendimiento_cereal.index[0]} ({rendimiento_cereal.values[0]:.2f} t/ha)
- **Tipos de cereales analizados:** {len(produccion_cereal)}

Comparando producción vs rendimiento, podemos identificar cereales con alta productividad.
""")

st.markdown("---")

# ==================== VISUALIZACIÓN 3: EVOLUCIÓN TEMPORAL ====================
st.markdown("## Visualización 3: Evolución Temporal de la Producción")

if 'año' in df_filtrado.columns and df_filtrado['año'].notna().sum() > 0:
    # Producción por año
    produccion_año = df_filtrado.groupby('año').agg({
        'produccion': 'sum',
        'area_sembrada': 'sum',
        'rendimiento': 'mean'
    }).reset_index()
    
    fig4 = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Producción y Área Sembrada por Año', 'Rendimiento Promedio por Año'),
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )
    
    # Gráfico 1: Producción y Área
    fig4.add_trace(
        go.Scatter(x=produccion_año['año'], y=produccion_año['produccion']/1000,
                   name='Producción (K ton)', line=dict(color='green', width=3)),
        row=1, col=1, secondary_y=False
    )
    fig4.add_trace(
        go.Scatter(x=produccion_año['año'], y=produccion_año['area_sembrada']/1000,
                   name='Área Sembrada (K ha)', line=dict(color='orange', width=3, dash='dash')),
        row=1, col=1, secondary_y=True
    )
    
    # Gráfico 2: Rendimiento
    fig4.add_trace(
        go.Scatter(x=produccion_año['año'], y=produccion_año['rendimiento'],
                   name='Rendimiento (t/ha)', line=dict(color='blue', width=3),
                   fill='tozeroy'),
        row=2, col=1
    )
    
    fig4.update_xaxes(title_text="Año", row=2, col=1)
    fig4.update_yaxes(title_text="Producción (K ton)", row=1, col=1, secondary_y=False)
    fig4.update_yaxes(title_text="Área (K ha)", row=1, col=1, secondary_y=True)
    fig4.update_yaxes(title_text="Rendimiento (t/ha)", row=2, col=1)
    
    fig4.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig4, use_container_width=True)
    
    # Cálculo de tendencias
    años_total = produccion_año['año'].nunique()
    prod_inicio = produccion_año.iloc[0]['produccion']
    prod_fin = produccion_año.iloc[-1]['produccion']
    cambio_porcentual = ((prod_fin - prod_inicio) / prod_inicio * 100) if prod_inicio > 0 else 0
    
    st.markdown(f"""
    ### Análisis Temporal
    - **Período analizado:** {int(produccion_año['año'].min())} - {int(produccion_año['año'].max())} ({años_total} años)
    - **Cambio en producción:** {cambio_porcentual:+.1f}%
    - **Tendencia:** {'Creciente' if cambio_porcentual > 5 else 'Decreciente' if cambio_porcentual < -5 else 'Estable'}
    
    La evolución temporal permite identificar tendencias de crecimiento o decrecimiento en la producción cerealera.
    """)
else:
    st.warning("⚠️ No hay datos temporales disponibles en el filtro actual.")

st.markdown("---")

# ==================== VISUALIZACIÓN 4: SISTEMAS PRODUCTIVOS ====================
st.markdown("## Visualización 4: Comparación de Sistemas Productivos")

if 'sistema_productivo' in df_filtrado.columns and df_filtrado['sistema_productivo'].notna().sum() > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        # Producción por sistema productivo (ranking completo)
        sistemas = df_filtrado.groupby('sistema_productivo')['produccion'].sum().sort_values(ascending=False)
        
        fig5 = px.bar(
            x=sistemas.values / 1000,
            y=sistemas.index,
            orientation='h',
            title='Ranking Completo de Sistemas Productivos por Producción',
            labels={'x': 'Producción (K ton)', 'y': 'Sistema Productivo'},
            color=sistemas.values,
            color_continuous_scale='Blues'
        )
        fig5.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        # Rendimiento por sistema productivo (ranking completo)
        rend_sistemas = df_filtrado.groupby('sistema_productivo')['rendimiento'].mean().sort_values(ascending=False)
        
        fig6 = px.bar(
            x=rend_sistemas.index,
            y=rend_sistemas.values,
            title='Ranking Completo de Sistemas por Rendimiento Promedio',
            labels={'x': 'Sistema Productivo', 'y': 'Rendimiento (t/ha)'},
            color=rend_sistemas.values,
            color_continuous_scale='RdYlGn'
        )
        fig6.update_layout(height=600, showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig6, use_container_width=True)
    
    st.markdown(f"""
    ### Análisis de Sistemas Productivos
    - **Sistemas identificados:** {df_filtrado['sistema_productivo'].nunique()}
    - **Sistema más productivo:** {sistemas.index[0]}
    - **Mayor rendimiento:** {rend_sistemas.index[0]} ({rend_sistemas.values[0]:.2f} t/ha)
    
    Diferentes sistemas productivos (riego, secano, tecnificado) muestran variaciones en eficiencia.
    """)
else:
    st.info("ℹ️ No hay datos de sistemas productivos disponibles en el filtro actual.")

st.markdown("---")

# ==================== TABLA DE DATOS ====================
st.markdown("## Tabla de Datos Completos")

with st.expander("Ver datos detallados (primeras 100 filas)"):
    st.dataframe(
        df_filtrado[['cultivo', 'departamento', 'municipio', 'año', 
                     'area_sembrada', 'area_cosechada', 'produccion', 'rendimiento']].head(100),
        use_container_width=True
    )
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar datos completos (CSV)",
        data=csv,
        file_name=f'cereales_completo_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )

st.markdown("---")

# ==================== DOCUMENTACIÓN DE DATOS ====================
st.markdown("## Documentación y Fuente de Datos")

with st.expander("Información sobre la fuente de datos y actualización"):
    st.markdown("""
    ### Fuente de Datos
    
    **Origen:** Evaluaciones Agropecuarias Municipales (EVA) - Ministerio de Agricultura y Desarrollo Rural de Colombia
    
    **URL de acceso:** 
    ```
    https://www.dropbox.com/scl/fi/e3iwe3z3jszouxues5bai/data21022026.csv
    ```
    
    **Fecha de acceso:** 24 de febrero de 2026
    
    **Última actualización de datos:** Febrero 2026
    
    ---
    
    ### Actualización de Datos
    
    **Frecuencia recomendada:** Trimestral o según publicación del Ministerio de Agricultura
    
    **Proceso de actualización:**
    1. Descargar el archivo CSV actualizado desde la fuente oficial del Ministerio
    2. Subir el archivo actualizado al mismo enlace de Dropbox (o actualizar la URL en el código)
    3. El dashboard se actualizará automáticamente al recargar la página
    
    **Contacto para actualizaciones:** Ministerio de Agricultura y Desarrollo Rural - Colombia
    
    ---
    
    ### Descripción del Dataset
    
    - **Registros totales (cereales):** {len(df):,}
    - **Registros filtrados actualmente:** {len(df_filtrado):,}
    - **Variables:** {len(df.columns)}
    - **Período temporal:** {int(df['año'].min()) if 'año' in df.columns else 'N/A'} - {int(df['año'].max()) if 'año' in df.columns else 'N/A'}
    - **Cereales incluidos:** {', '.join(sorted(df['cultivo'].unique()))}
    - **Departamentos cubiertos:** {df['departamento'].nunique()}
    - **Municipios cubiertos:** {df['municipio'].nunique()}
    
    ---
    
    ### Créditos
    
    **Desarrollado por:** Grupo 2 - MAD (Métodos Analíticos de Datos)
    
    **Fecha de desarrollo:** Febrero 2026
    
    **Herramientas utilizadas:** Python, Streamlit, Plotly, Pandas
    
    **Framework de análisis:** EDA QUEST (Question, Understand, Explore, Scrutinize, Transform)
    """)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p>Dashboard de Producción de Cereales en Colombia | Grupo 2 MAD | 2026</p>
    <p><small>Desarrollado con Streamlit | Datos: Ministerio de Agricultura de Colombia</small></p>
</div>
""", unsafe_allow_html=True)
