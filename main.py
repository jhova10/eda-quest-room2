"""
Dashboard Interactivo: Producción de Arroz en Colombia
Análisis Exploratorio de Datos (EDA) - Enfoque: De Macro a Específico
Grupo 2 MAD
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
    page_title="Dashboard Arroz Colombia",
    page_icon="🍚",
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
    """Carga y preprocesa los datos de arroz desde Dropbox"""
    url = 'https://www.dropbox.com/scl/fi/e3iwe3z3jszouxues5bai/data21022026.csv?rlkey=fb1ex5sbf7yz4p0im8gfiziwm&st=va67mghf&dl=1'
    
    # Cargar dataset completo
    df_completo = pd.read_csv(url, delimiter=';', encoding='utf-8')
    
    # Limpiar nombres de columnas
    df_completo.columns = df_completo.columns.str.strip().str.replace('\n', ' ')
    
    # Filtrar solo ARROZ
    df = df_completo[
        (df_completo['GRUPO  DE CULTIVO'].str.strip().str.upper() == 'CEREALES') &
        (df_completo['CULTIVO'].str.strip().str.upper() == 'ARROZ')
    ].copy()
    
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
with st.spinner('Cargando datos de arroz...'):
    df = load_data()

# ==================== SIDEBAR - FILTROS INTERACTIVOS ====================
st.sidebar.markdown("## Filtros Interactivos")
st.sidebar.markdown("---")

# Filtro de Departamentos
departamentos_disponibles = sorted(df['departamento'].unique())
departamentos_seleccionados = st.sidebar.multiselect(
    "Selecciona Departamentos:",
    options=departamentos_disponibles,
    default=departamentos_disponibles,  # Todos seleccionados por defecto
    help="Selecciona departamentos para filtrar"
)

st.sidebar.markdown("---")
st.sidebar.info("Todos los departamentos están seleccionados por defecto. Modifica los filtros para personalizar tu análisis.")

# ==================== APLICAR FILTROS ====================
df_filtrado = df.copy()

# Aplicar filtro de departamentos
if departamentos_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['departamento'].isin(departamentos_seleccionados)]

# Validar que hay datos después de filtrar
if df_filtrado.empty:
    st.error("No hay datos disponibles con los filtros seleccionados. Por favor, ajusta tus selecciones.")
    st.stop()

# ==================== HEADER ====================
st.markdown('<div class="main-header">Dashboard: Producción de Arroz en Colombia</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h3>Contexto del Dashboard - EDA de Macro a Específico</h3>
    <p><strong>Objetivo:</strong> Analizar la producción de arroz en Colombia mediante un enfoque estructurado 
    que va de lo general a lo particular, utilizando datos de las Evaluaciones Agropecuarias Municipales (EVA) 
    del Ministerio de Agricultura.</p>
    <p><strong>Preguntas Analíticas:</strong></p>
    <ul>
        <li>¿Cómo ha evolucionado la producción de arroz a lo largo del tiempo? (Macro - Temporal)</li>
        <li>¿Cuál es la distribución geográfica de la producción? (Macro - Espacial)</li>
        <li>¿Qué sistemas productivos se utilizan y cuál es su eficiencia? (Específico - Sistemas)</li>
        <li>¿Cómo se comparan los rendimientos entre regiones? (Específico - Rendimientos)</li>
    </ul>
    <p><strong>Instrucciones:</strong> Las visualizaciones están organizadas de lo macro (visión general) a lo específico (detalles). 
    Utiliza los filtros para personalizar tu análisis.</p>
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

# ==================== FILTROS ADICIONALES ====================
st.markdown("## Filtros de Análisis")

col_filtro_año = st.columns([1, 2])[0]

with col_filtro_año:
    # Filtro de Año específico
    if 'año' in df_filtrado.columns and df_filtrado['año'].notna().any():
        años_filtro = sorted(df_filtrado['año'].dropna().unique(), reverse=True)
        año_analisis = st.selectbox(
            "Selecciona Año para Análisis:",
            options=['Todos'] + [int(a) for a in años_filtro],
            index=0,  # Índice 0 = "Todos"
            help="Filtra los datos por un año específico. Por defecto muestra todos los años."
        )
    else:
        año_analisis = 'Todos'

# Aplicar filtro de año
if año_analisis != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['año'] == año_analisis]

# Validar que hay datos después de aplicar filtros adicionales
if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles con los filtros seleccionados. Por favor, ajusta tus selecciones.")
    st.stop()

st.markdown("---")

# ==================== VISUALIZACIÓN 1: EVOLUCIÓN TEMPORAL (MACRO) ====================
st.markdown("## Visualización 1: Evolución Temporal de la Producción de Arroz (Visión Macro)")

if 'año' in df_filtrado.columns and df_filtrado['año'].notna().sum() > 0:
    # Producción por año
    produccion_año = df_filtrado.groupby('año').agg({
        'produccion': 'sum',
        'area_sembrada': 'sum',
        'rendimiento': 'mean'
    }).reset_index()
    
    fig1 = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Producción y Área Sembrada por Año', 'Rendimiento Promedio por Año'),
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
    )
    
    # Gráfico 1: Producción y Área
    fig1.add_trace(
        go.Scatter(x=produccion_año['año'], y=produccion_año['produccion']/1000,
                   name='Producción (K ton)', line=dict(color='green', width=3)),
        row=1, col=1, secondary_y=False
    )
    fig1.add_trace(
        go.Scatter(x=produccion_año['año'], y=produccion_año['area_sembrada']/1000,
                   name='Área Sembrada (K ha)', line=dict(color='orange', width=3, dash='dash')),
        row=1, col=1, secondary_y=True
    )
    
    # Gráfico 2: Rendimiento
    fig1.add_trace(
        go.Scatter(x=produccion_año['año'], y=produccion_año['rendimiento'],
                   name='Rendimiento (t/ha)', line=dict(color='blue', width=3),
                   fill='tozeroy'),
        row=2, col=1
    )
    
    fig1.update_xaxes(title_text="Año", row=2, col=1)
    fig1.update_yaxes(title_text="Producción (K ton)", row=1, col=1, secondary_y=False)
    fig1.update_yaxes(title_text="Área (K ha)", row=1, col=1, secondary_y=True)
    fig1.update_yaxes(title_text="Rendimiento (t/ha)", row=2, col=1)
    
    fig1.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Cálculo de tendencias
    años_total = produccion_año['año'].nunique()
    prod_inicio = produccion_año.iloc[0]['produccion']
    prod_fin = produccion_año.iloc[-1]['produccion']
    cambio_porcentual = ((prod_fin - prod_inicio) / prod_inicio * 100) if prod_inicio > 0 else 0
    
    st.markdown(f"""
    ### Análisis Temporal (Macro)
    - **Período analizado:** {int(produccion_año['año'].min())} - {int(produccion_año['año'].max())} ({años_total} años)
    - **Cambio en producción:** {cambio_porcentual:+.1f}%
    - **Tendencia:** {'Creciente' if cambio_porcentual > 5 else 'Decreciente' if cambio_porcentual < -5 else 'Estable'}
    - **Producción promedio anual:** {produccion_año['produccion'].mean()/1000:.1f}K ton
    
    Esta visión macro muestra la evolución histórica de la producción arrocera en Colombia.
    """)
else:
    st.warning("⚠️ No hay datos temporales disponibles.")

st.markdown("---")

# ==================== VISUALIZACIÓN 2: DISTRIBUCIÓN GEOGRÁFICA (MACRO) ====================
st.markdown("## Visualización 2: Distribución Geográfica de la Producción de Arroz (Visión Macro)")

col1, col2 = st.columns([2, 1])

with col1:
    # Producción por departamento - Ranking completo (mayor a menor, de arriba hacia abajo)
    produccion_dep = df_filtrado.groupby('departamento')['produccion'].sum().sort_values(ascending=True)  # Invertido para gráfico horizontal
    
    fig2 = px.bar(
        x=produccion_dep.values / 1000,
        y=produccion_dep.index,
        orientation='h',
        title='Ranking Completo de Departamentos por Producción de Arroz',
        labels={'x': 'Producción (miles de toneladas)', 'y': 'Departamento'},
        color=produccion_dep.values,
        color_continuous_scale='Greens'
    )
    fig2.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("### Interpretación Macro")
    produccion_dep_desc = produccion_dep.sort_values(ascending=False)  # Para mostrar estadísticas correctas
    st.markdown(f"""
    - **Departamentos productores:** {df_filtrado['departamento'].nunique()}
    - **Líder en producción:** {produccion_dep_desc.index[0]}
    - **Producción líder:** {produccion_dep_desc.values[0]/1000:.1f}K ton
    - **Concentración:** Los top 5 representan el {(produccion_dep_desc.head(5).sum() / produccion_dep_desc.sum() * 100):.1f}% del total
    
    Esta visión macro muestra la distribución espacial de la producción arrocera en Colombia.
    """)

st.markdown("---")

# ==================== VISUALIZACIÓN 3: SISTEMAS PRODUCTIVOS (ESPECÍFICO) ====================
st.markdown("## Visualización 3: Sistemas Productivos de Arroz (Análisis Específico)")

if 'sistema_productivo' in df_filtrado.columns and df_filtrado['sistema_productivo'].notna().sum() > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        # Producción por sistema productivo (ranking completo, mayor arriba)
        sistemas = df_filtrado.groupby('sistema_productivo')['produccion'].sum().sort_values(ascending=True)  # Invertido para gráfico horizontal
        
        fig3 = px.bar(
            x=sistemas.values / 1000,
            y=sistemas.index,
            orientation='h',
            title='Ranking de Sistemas Productivos por Producción',
            labels={'x': 'Producción (K ton)', 'y': 'Sistema Productivo'},
            color=sistemas.values,
            color_continuous_scale='Blues'
        )
        fig3.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Rendimiento por sistema productivo (ranking completo, mayor a menor)
        rend_sistemas = df_filtrado.groupby('sistema_productivo')['rendimiento'].mean().sort_values(ascending=False)
        
        fig4 = px.bar(
            x=rend_sistemas.index,
            y=rend_sistemas.values,
            title='Ranking de Sistemas por Rendimiento Promedio',
            labels={'x': 'Sistema Productivo', 'y': 'Rendimiento (t/ha)'},
            color=rend_sistemas.values,
            color_continuous_scale='RdYlGn'
        )
        fig4.update_layout(height=600, showlegend=False, xaxis_tickangle=-45, xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig4, use_container_width=True)
    
    sistemas_desc = sistemas.sort_values(ascending=False)  # Para estadísticas correctas
    st.markdown(f"""
    ### Análisis de Sistemas Productivos (Específico)
    - **Sistemas identificados:** {df_filtrado['sistema_productivo'].nunique()}
    - **Sistema más productivo:** {sistemas_desc.index[0]}
    - **Mayor rendimiento:** {rend_sistemas.index[0]} ({rend_sistemas.values[0]:.2f} t/ha)
    
    Este análisis específico muestra las diferencias en eficiencia entre sistemas productivos de arroz (riego, secano, mecanizado, etc.).
    """)
else:
    st.info("ℹ️ No hay datos de sistemas productivos disponibles.")

st.markdown("---")

# ==================== TABLA DE DATOS ====================
st.markdown("## Tabla de Datos Filtrados")

with st.expander("Ver datos detallados (primeras 100 filas)"):
    st.dataframe(
        df_filtrado[['cultivo', 'departamento', 'municipio', 'año', 
                     'area_sembrada', 'area_cosechada', 'produccion', 'rendimiento']].head(100),
        use_container_width=True
    )
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar datos filtrados (CSV)",
        data=csv,
        file_name=f'cereales_filtrado_{datetime.now().strftime("%Y%m%d")}.csv',
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
    
    **Cultivo analizado:** Arroz (filtrado desde el dataset completo de cereales)
    
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
    
    - **Registros totales (arroz):** {len(df):,}
    - **Registros filtrados actualmente:** {len(df_filtrado):,}
    - **Variables:** {len(df.columns)}
    - **Período temporal:** {int(df['año'].min()) if 'año' in df.columns else 'N/A'} - {int(df['año'].max()) if 'año' in df.columns else 'N/A'}
    - **Cultivo:** Arroz
    - **Departamentos cubiertos:** {df['departamento'].nunique()}
    - **Municipios cubiertos:** {df['municipio'].nunique()}
    
    ---
    
    ### Enfoque Metodológico
    
    **EDA de Macro a Específico:**
    1. **Nivel Macro - Temporal:** Evolución histórica de la producción
    2. **Nivel Macro - Espacial:** Distribución geográfica por departamentos
    3. **Nivel Específico:** Análisis de sistemas productivos y rendimientos
    
    Este enfoque permite comprender primero el panorama general antes de profundizar en detalles específicos.
    
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
    <p>Dashboard de Producción de Arroz en Colombia - EDA de Macro a Específico | Grupo 2 MAD | 2026</p>
    <p><small>Desarrollado con Streamlit | Datos: Ministerio de Agricultura de Colombia</small></p>
</div>
""", unsafe_allow_html=True)
