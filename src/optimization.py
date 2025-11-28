import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from src import calculations

def render_optimization_section(df, config):
    """
    Renders the optimization section (Efficient Frontier, CML, Optimized Portfolio).
    """
    st.markdown("### Optimización y Frontera Eficiente")
    
    if df is None or config is None:
        st.warning("Por favor complete la configuración en la sección anterior.")
        return None

    selected_assets = config['assets']
    rf_rate_monthly = config['rf_rate_monthly']
    forced_weights = config.get('forced_weights', {})
    
    # Filter data for selected assets
    asset_data = df[selected_assets]
    
    # Calculate returns
    returns = calculations.calculate_returns(asset_data)
    
    # Calculate metrics
    mean_ret, vol, sharpe = calculations.calculate_metrics(returns, rf_rate_monthly)
    
    # Calculate Covariance Matrix
    cov_matrix = calculations.calculate_covariance_matrix(returns)
    
    # 1. Optimize Portfolio
    st.subheader("1. Portafolio Optimizado (Máximo Sharpe)")
    
    with st.spinner("Optimizando portafolio..."):
        opt_result = calculations.optimize_portfolio(
            mean_ret, 
            cov_matrix, 
            rf_rate_monthly,
            forced_weights=forced_weights,
            asset_names=selected_assets
        )
    
    if not opt_result['success']:
        st.error(f"Error en la optimización: {opt_result['message']}")
        return None
    
    st.success("Optimización completada exitosamente!")
    
    # Display optimized metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rendimiento Anual", f"{opt_result['return']:.2%}")
    with col2:
        st.metric("Volatilidad Anual", f"{opt_result['volatility']:.2%}")
    with col3:
        st.metric("Ratio de Sharpe", f"{opt_result['sharpe']:.3f}")
    
    # 2. Calculate Efficient Frontier
    st.subheader("2. Frontera Eficiente")
    
    with st.spinner("Calculando frontera eficiente..."):
        ef_df = calculations.calculate_efficient_frontier(mean_ret, cov_matrix, num_points=50)
    
    # Calculate Equal Weights Portfolio for comparison
    num_assets = len(selected_assets)
    equal_weights = [1/num_assets] * num_assets
    eq_return, eq_vol, eq_sharpe = calculations.calculate_portfolio_performance(
        equal_weights, 
        mean_ret, 
        cov_matrix, 
        rf_rate_monthly
    )
    
    # 3. Plot Efficient Frontier
    fig = go.Figure()
    
    # Efficient Frontier Curve
    fig.add_trace(go.Scatter(
        x=ef_df['volatility'],
        y=ef_df['return'],
        mode='lines',
        name='Frontera Eficiente',
        line=dict(color='cyan', width=3),
        hovertemplate='Volatilidad: %{x:.2%}<br>Rendimiento: %{y:.2%}<extra></extra>'
    ))
    
    # Equal Weights Portfolio Point
    fig.add_trace(go.Scatter(
        x=[eq_vol],
        y=[eq_return],
        mode='markers',
        name='Portafolio Pesos Iguales',
        marker=dict(size=12, color='yellow', symbol='circle'),
        hovertemplate='Pesos Iguales<br>Volatilidad: %{x:.2%}<br>Rendimiento: %{y:.2%}<extra></extra>'
    ))
    
    # Optimized Portfolio Point
    fig.add_trace(go.Scatter(
        x=[opt_result['volatility']],
        y=[opt_result['return']],
        mode='markers',
        name='Portafolio Optimizado',
        marker=dict(size=15, color='lime', symbol='star'),
        hovertemplate='Optimizado<br>Volatilidad: %{x:.2%}<br>Rendimiento: %{y:.2%}<extra></extra>'
    ))
    
    # Capital Market Line (CML)
    rf_rate_annual = (1 + rf_rate_monthly)**12 - 1
    
    # CML: y = rf + (sharpe_opt) * x
    max_vol = ef_df['volatility'].max() * 1.2
    cml_x = np.linspace(0, max_vol, 100)
    cml_y = rf_rate_annual + opt_result['sharpe'] * cml_x
    
    fig.add_trace(go.Scatter(
        x=cml_x,
        y=cml_y,
        mode='lines',
        name='Línea del Mercado de Capitales (CML)',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='CML<br>Volatilidad: %{x:.2%}<br>Rendimiento: %{y:.2%}<extra></extra>'
    ))
    
    # Layout
    fig.update_layout(
        title="Frontera Eficiente y Línea del Mercado de Capitales",
        xaxis_title="Volatilidad (Riesgo)",
        yaxis_title="Rendimiento Esperado",
        template="plotly_dark",
        hovermode='closest',
        xaxis=dict(tickformat='.1%'),
        yaxis=dict(tickformat='.1%')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Store optimized result in session state
    st.session_state['opt_result'] = opt_result
    
    return opt_result
