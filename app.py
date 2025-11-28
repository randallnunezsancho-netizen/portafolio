import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(
    page_title="Portafolio de Inversión",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("assets/style.css")
except FileNotFoundError:
    st.warning("Archivo de estilos no encontrado. Asegúrese de que 'assets/style.css' exista.")

# Sidebar Navigation
st.sidebar.title("Navegación")
selection = st.sidebar.radio("Ir a:", [
    "Inicio",
    "Carga de Datos",
    "Configuración",
    "Análisis",
    "Optimización",
    "Resultados"
])

# Main Content
st.title("Portafolio de Inversión con Optimización de Markowitz")

if selection == "Inicio":
    st.markdown("""
    ### Bienvenido
    Esta aplicación permite analizar y optimizar un portafolio de inversión utilizando datos históricos.
    
    **Características:**
    - Análisis de 20 empresas + S&P 500.
    - Optimización de Markowitz (Python puro).
    - Visualización interactiva.
    """)

elif selection == "Carga de Datos":
    st.header("Carga y Preparación de Datos")
    
    from src import data
    
    file_path = "datos/portafolio_21_activos.csv"
    
    if 'data' not in st.session_state:
        st.session_state['data'] = None
        
    if st.button("Cargar Datos"):
        with st.spinner("Cargando datos..."):
            raw_df = data.load_data(file_path)
            
            if raw_df is not None:
                clean_df, removed_assets = data.clean_data(raw_df)
                st.session_state['data'] = clean_df
                st.session_state['removed_assets'] = removed_assets
                st.success("Datos cargados exitosamente!")
            else:
                st.error(f"No se pudo cargar el archivo: {file_path}")

    if st.session_state.get('data') is not None:
        st.subheader("Datos Cargados (Limpios)")
        st.dataframe(st.session_state['data'].head())
        
        st.subheader("Resumen de Limpieza")
        if st.session_state['removed_assets']:
            st.warning(f"Se omitieron los siguientes activos por datos incompletos: {', '.join(st.session_state['removed_assets'])}")
        else:
            st.info("Todos los activos tienen datos completos.")
            
        st.write(f"Total de activos válidos: {len(st.session_state['data'].columns)}")


elif selection == "Configuración":
    st.header("Inputs y Configuración")
    
    from src import inputs
    
    if st.session_state.get('data') is None:
        st.warning("Por favor cargue los datos primero en la sección 'Carga de Datos'.")
    else:
        config = inputs.render_inputs_section(st.session_state['data'])
        
        if config:
            st.info(f"Configuración actual: {len(config['assets'])} activos seleccionados, Tasa RF: {config['rf_rate_annual']:.1%}")


elif selection == "Análisis":
    st.header("Análisis de Riesgos")
    
    from src import analysis
    
    if st.session_state.get('data') is None:
        st.warning("Por favor cargue los datos primero.")
    elif st.session_state.get('config') is None:
        st.warning("Por favor configure el portafolio primero.")
    else:
        analysis.render_analysis_section(st.session_state['data'], st.session_state['config'])


elif selection == "Optimización":
    st.header("Frontera Eficiente")
    
    from src import optimization
    
    if st.session_state.get('data') is None:
        st.warning("Por favor cargue los datos primero.")
    elif st.session_state.get('config') is None:
        st.warning("Por favor configure el portafolio primero.")
    else:
        optimization.render_optimization_section(st.session_state['data'], st.session_state['config'])


elif selection == "Resultados":
    st.header("Resultados Finales")
    st.info("Módulo en construcción...")
