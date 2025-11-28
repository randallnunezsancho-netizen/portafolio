import numpy as np
import pandas as pd

def calculate_returns(df):
    """
    Calculates daily returns.
    """
    return df.pct_change().dropna()

def calculate_metrics(returns, rf_rate_monthly):
    """
    Calculates annualized return, volatility, and Sharpe ratio.
    Assumes monthly data input.
    """
    # Annualize factor for monthly data
    ann_factor = 12
    
    # Expected Return (Annualized)
    mean_return = returns.mean() * ann_factor
    
    # Volatility (Annualized)
    volatility = returns.std() * np.sqrt(ann_factor)
    
    # Sharpe Ratio
    sharpe_ratio = (mean_return - rf_rate_monthly * ann_factor) / volatility
    
    return mean_return, volatility, sharpe_ratio

def calculate_covariance_matrix(returns):
    """
    Calculates the covariance matrix (annualized).
    """
    return returns.cov() * 12

def calculate_portfolio_performance(weights, mean_returns, cov_matrix, rf_rate_monthly):
    """
    Calculates the annualized performance of a portfolio.
    
    Args:
        weights (np.array): Asset weights.
        mean_returns (pd.Series): Annualized mean returns of assets.
        cov_matrix (pd.DataFrame): Annualized covariance matrix.
        rf_rate_monthly (float): Monthly risk-free rate.
        
    Returns:
        tuple: (Expected Return, Volatility, Sharpe Ratio)
    """
    # Annualize factor (already applied to inputs usually, but let's be consistent)
    # Assuming mean_returns and cov_matrix are ALREADY annualized
    
    weights = np.array(weights)
    
    # Portfolio Return
    port_return = np.sum(mean_returns * weights)
    
    # Portfolio Volatility
    port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    port_volatility = np.sqrt(port_variance)
    
    # Portfolio Sharpe Ratio
    # Convert monthly RF to annual for Sharpe calculation consistency with annualized metrics
    rf_rate_annual = (1 + rf_rate_monthly)**12 - 1
    
    sharpe_ratio = (port_return - rf_rate_annual) / port_volatility
    
    return port_return, port_volatility, sharpe_ratio

from scipy.optimize import minimize

def optimize_portfolio(mean_returns, cov_matrix, rf_rate_monthly, forced_weights=None, asset_names=None):
    """
    Optimizes the portfolio to maximize Sharpe Ratio.
    
    Args:
        mean_returns (pd.Series): Annualized mean returns.
        cov_matrix (pd.DataFrame): Annualized covariance matrix.
        rf_rate_monthly (float): Monthly risk-free rate.
        forced_weights (dict): Dictionary of {asset_name: weight}.
        asset_names (list): List of asset names (columns of cov_matrix).
        
    Returns:
        dict: Optimization result containing 'weights', 'return', 'volatility', 'sharpe'.
    """
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, rf_rate_monthly)
    
    # Objective Function: Negative Sharpe Ratio (since we minimize)
    def neg_sharpe_ratio(weights, mean_returns, cov_matrix, rf_rate_monthly):
        p_ret, p_vol, p_sharpe = calculate_portfolio_performance(weights, mean_returns, cov_matrix, rf_rate_monthly)
        return -p_sharpe
    
    # Constraints
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # Bounds
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    
    # Apply Forced Weights if any
    if forced_weights and asset_names:
        new_bounds = list(bounds)
        for asset, weight in forced_weights.items():
            if asset in asset_names:
                idx = asset_names.index(asset)
                new_bounds[idx] = (weight, weight) # Fix weight
        bounds = tuple(new_bounds)

    # Initial Guess (Equal Weights)
    initial_guess = num_assets * [1. / num_assets,]
    
    # Optimization
    result = minimize(
        neg_sharpe_ratio,
        initial_guess,
        args=args,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    # Extract results
    opt_weights = result.x
    opt_ret, opt_vol, opt_sharpe = calculate_portfolio_performance(opt_weights, mean_returns, cov_matrix, rf_rate_monthly)
    
    return {
        'weights': opt_weights,
        'return': opt_ret,
        'volatility': opt_vol,
        'sharpe': opt_sharpe,
        'success': result.success,
        'message': result.message
    }

def calculate_efficient_frontier(mean_returns, cov_matrix, num_points=50):
    """
    Calculates the Efficient Frontier.
    """
    num_assets = len(mean_returns)
    
    # 1. Find Min Volatility Portfolio
    def portfolio_volatility(weights, mean_returns, cov_matrix):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    initial_guess = num_assets * [1. / num_assets,]
    
    min_vol_result = minimize(
        portfolio_volatility,
        initial_guess,
        args=(mean_returns, cov_matrix),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    min_vol = min_vol_result.fun
    min_vol_ret = np.sum(mean_returns * min_vol_result.x)
    
    # 2. Find Max Return Portfolio (roughly)
    max_ret = mean_returns.max()
    
    # 3. Calculate points between Min Vol Ret and Max Ret
    target_returns = np.linspace(min_vol_ret, max_ret, num_points)
    efficient_frontier = []
    
    for target in target_returns:
        constraints_target = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.sum(mean_returns * x) - target}
        )
        
        result = minimize(
            portfolio_volatility,
            initial_guess,
            args=(mean_returns, cov_matrix),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_target
        )
        
        if result.success:
            efficient_frontier.append({
                'return': target,
                'volatility': result.fun,
                'sharpe': (target - 0.04) / result.fun # Approximate Sharpe for visualization coloring
            })
            
    return pd.DataFrame(efficient_frontier)
