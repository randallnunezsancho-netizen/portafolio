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
