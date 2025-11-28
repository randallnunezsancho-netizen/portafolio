import streamlit as st

def render_inputs_section(df):
    """
    Renders the inputs and configuration section.
    
    Args:
        df (pd.DataFrame): The loaded data dataframe.
        
    Returns:
        dict: A dictionary containing the configuration (selected assets, risk-free rate, etc.)
    """
    st.markdown("### Configuración del Portafolio")
    
    if df is None:
        st.error("No hay datos cargados. Por favor vaya a la sección 'Carga de Datos'.")
        return None

    all_assets = [col for col in df.columns if col != '^GSPC']
    
    # 1. Asset Selection
    st.subheader("1. Selección de Activos")
    selected_assets = st.multiselect(
        "Seleccione los activos para el portafolio:",
        options=all_assets,
        default=all_assets  # Select all by default
    )
    
    if not selected_assets:
        st.warning("Debe seleccionar al menos un activo.")
        return None

    # 2. Forced Weights (Optional)
    st.subheader("2. Pesos Forzados (Opcional)")
    st.markdown("Asigne pesos específicos a los activos. Deje en 0 para que el optimizador decida.")
    
    forced_weights = {}
    total_forced_weight = 0.0
    
    with st.expander("Configurar Pesos Manuales"):
        cols = st.columns(3)
        for i, asset in enumerate(selected_assets):
            with cols[i % 3]:
                weight = st.number_input(
                    f"{asset} (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    key=f"weight_{asset}"
                )
                if weight > 0:
                    forced_weights[asset] = weight / 100.0
                    total_forced_weight += weight

    # Validation: Check if total forced weight > 100%
    if total_forced_weight > 100.0:
        st.error(f"⚠️ Error: La suma de los pesos forzados es {total_forced_weight:.2f}%, no puede exceder el 100%.")
        return None
    
    if total_forced_weight > 0:
        st.info(f"Peso total asignado manualmente: **{total_forced_weight:.2f}%**. El optimizador distribuirá el {100 - total_forced_weight:.2f}% restante.")

    # 3. Risk-Free Rate
    st.subheader("3. Tasa Libre de Riesgo")
    rf_rate_annual = st.number_input(
        "Tasa Libre de Riesgo Anual (%)",
        min_value=0.0,
        max_value=20.0,
        value=4.0,
        step=0.01,
        format="%.2f",
        help="Tasa de rendimiento de un activo sin riesgo (ej. Bonos del Tesoro a 10 años)."
    )
    
    # Convert to monthly
    rf_rate_monthly = (1 + rf_rate_annual/100)**(1/12) - 1
    
    st.write(f"Tasa mensual calculada: **{rf_rate_monthly:.4%}**")

    # 4. Confirmation
    st.subheader("4. Confirmación")
    if st.button("Confirmar Configuración"):
        config = {
            "assets": selected_assets,
            "forced_weights": forced_weights,
            "rf_rate_annual": rf_rate_annual / 100,
            "rf_rate_monthly": rf_rate_monthly
        }
        st.session_state['config'] = config
        st.success(f"Configuración guardada. {len(selected_assets)} activos seleccionados.")
        return config
    
    if 'config' in st.session_state:
        return st.session_state['config']
    
    return None
