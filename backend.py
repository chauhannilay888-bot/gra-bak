import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

def smart_clean_df(df):
    if df is None or df.empty:
        return df
    
    # Downcast for RAM efficiency
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')

    df_clean = df.copy()
    if df_clean.isnull().values.any():
        for column in df_clean.columns:
            if df_clean[column].isnull().any():
                if pd.api.types.is_numeric_dtype(df_clean[column]):
                    mean_val = df_clean[column].mean()
                    df_clean[column] = df_clean[column].fillna(mean_val if pd.notnull(mean_val) else 0)
                else:
                    mode_vals = df_clean[column].mode()
                    df_clean[column] = df_clean[column].fillna(mode_vals[0] if not mode_vals.empty else "Unknown")
    return df_clean

def encode_column(df, column, encoding_type="Label Encoding"):
    df_preview = df.copy()
    if encoding_type == "Label Encoding":
        le = LabelEncoder()
        encd_name = str(column) + "_encoded"
        df_preview[encd_name] = le.fit_transform(df_preview[column].astype(str))
    elif encoding_type == "One-Hot Encoding":
        df_preview = pd.get_dummies(df_preview, columns=[column])
    return df_preview

def perform_prediction(df, feature_col, target_col, model_type="Linear Regression", poly_degree=2, predict_value=None):
    if not pd.api.types.is_numeric_dtype(df[feature_col]) or not pd.api.types.is_numeric_dtype(df[target_col]):
        raise ValueError("Feature and target must be numeric")
    
    X = df[[feature_col]]
    y = df[target_col]
    
    if model_type == "Linear Regression":
        model = LinearRegression()
        model.fit(X, y)
    else:
        model = make_pipeline(PolynomialFeatures(poly_degree), LinearRegression())
        model.fit(X, y)
    
    if predict_value is not None:
        pred = model.predict([[predict_value]])[0]
        return pred, model
    return None, model

def edit_dataframe(df, operation, **kwargs):
    df = df.copy()
    if operation == "remove_column":
        col = kwargs.get("column")
        if col in df.columns:
            df.drop(columns=[col], inplace=True)
    elif operation == "remove_row":
        idx = kwargs.get("index")
        if idx in df.index:
            df.drop(index=idx, inplace=True)
    elif operation == "update_cell":
        row = kwargs.get("row")
        col = kwargs.get("column")
        value = kwargs.get("value")
        if row in df.index and col in df.columns:
            df.at[row, col] = value
    return df