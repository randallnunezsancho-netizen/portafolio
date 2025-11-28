import pandas as pd
import os

def load_data(file_path):
    """
    Loads data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        pd.DataFrame: Loaded data as a DataFrame, or None if error.
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        df = pd.read_csv(file_path)
        # Ensure Date column is datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def clean_data(df):
    """
    Cleans the data by removing columns with missing values.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        tuple: (Cleaned DataFrame, List of removed assets)
    """
    if df is None:
        return None, []
    
    # Check for missing values
    missing_data = df.isnull().sum()
    columns_with_missing = missing_data[missing_data > 0].index.tolist()
    
    # Drop columns with missing values
    df_clean = df.drop(columns=columns_with_missing)
    
    return df_clean, columns_with_missing
