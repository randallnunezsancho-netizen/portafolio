import streamlit as st
import plotly.express as px
import pandas as pd
from src import calculations

def render_analysis_section(df, config):
    """
    Renders the analysis section (Correlation heatmap, metrics).
    """
    st.markdown("### Análisis de Riesgos y Dependencias")
    
    if df is None or config is None:
        st.warning("Por favor complete la configuración en la sección anterior.")
        return

    selected_assets = config['assets']
    rf_rate_monthly = config['rf_rate_monthly']
    
    # Filter data for selected assets
    asset_data = df[selected_assets]
    
    # Calculate returns
    returns = calculations.calculate_returns(asset_data)
    
    # 1. Correlation Matrix
    st.subheader("1. Matriz de Correlaciones")
    corr_matrix = returns.corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu',
        zmin=-1, zmax=1,
        title="Mapa de Calor de Correlaciones"
    )
    fig_corr.update_layout(template="plotly_dark")
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # 2. Individual Asset Metrics
    st.subheader("2. Métricas Individuales (Anualizadas)")
    
    mean_ret, vol, sharpe = calculations.calculate_metrics(returns, rf_rate_monthly)
    
    metrics_df = pd.DataFrame({
        "Rendimiento Esperado": mean_ret,
        "Volatilidad (Riesgo)": vol,
        "Ratio de Sharpe": sharpe
    })
    
    st.dataframe(metrics_df.style.format("{:.2%}"), use_container_width=True)
    
    st.info("Nota: Los cálculos asumen datos mensuales anualizados (x12).")
