import io
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from PIL import Image
from pathlib import Path
import base64
from typing import Dict, Any, Optional, Tuple, Union, List
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import streamlit as st

# Force Plotly to use dark template
px.defaults.template = "plotly_dark"[cite: 1]

# ====================== NETWORK SERIALIZATION HELPERS ======================

def payload_to_df(json_data: Union[str, List, Dict]) -> pd.DataFrame:
    """Convert incoming JSON/dict payload from network back into a live Pandas DataFrame."""
    try:
        if isinstance(json_data, str):
            return pd.read_json(io.StringIO(json_data))
        else:
            return pd.DataFrame.from_records(json_data)
    except Exception as e:
        st.error(f"Failed to parse incoming network data to DataFrame: {e}")
        return pd.DataFrame()

def df_to_payload(df: pd.DataFrame) -> List[Dict]:
    """Convert a processed DataFrame into a clean JSON-serializable list of dicts for network transmission."""
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")

# ====================== CORE UTILITIES ======================

def img_to_base64(image_path: str) -> str:[cite: 1]
    """Convert image to base64 (kept for potential internal use)."""[cite: 1]
    try:[cite: 1]
        img_bytes = Path(image_path).read_bytes()[cite: 1]
        encoded = base64.b64encode(img_bytes).decode("utf-8")[cite: 1]
        ext = image_path.lower().split(".")[-1][cite: 1]
        mime = "jpeg" if ext in ["jpg", "jpeg"] else ext[cite: 1]
        return f"data:image/{mime};base64,{encoded}"[cite: 1]
    except Exception:[cite: 1]
        return ""[cite: 1]


def smart_clean_df(df: pd.DataFrame) -> pd.DataFrame:[cite: 1]
    """BRAHMASTRA: Core data cleaning with memory optimization."""[cite: 1]
    if df is None or df.empty:[cite: 1]
        return df[cite: 1]

    # Downcast numeric types to save RAM[cite: 1]
    for col in df.select_dtypes(include=['float64']).columns:[cite: 1]
        df[col] = pd.to_numeric(df[col], downcast='float')[cite: 1]
    for col in df.select_dtypes(include=['int64']).columns:[cite: 1]
        df[col] = pd.to_numeric(df[col], downcast='integer')[cite: 1]

    df_clean = df.copy()[cite: 1]
    if df_clean.isnull().values.any():[cite: 1]
        for column in df_clean.columns:[cite: 1]
            if df_clean[column].isnull().any():[cite: 1]
                if pd.api.types.is_numeric_dtype(df_clean[column]):[cite: 1]
                    mean_val = df_clean[column].mean()[cite: 1]
                    df_clean[column] = df_clean[column].fillna([cite: 1]
                        mean_val if pd.notnull(mean_val) else 0[cite: 1]
                    )[cite: 1]
                else:[cite: 1]
                    mode_vals = df_clean[column].mode()[cite: 1]
                    df_clean[column] = df_clean[column].fillna([cite: 1]
                        mode_vals[0] if not mode_vals.empty else "Unknown"[cite: 1]
                    )[cite: 1]
    return df_clean[cite: 1]


# ====================== DATA LOADING ======================

def load_data_from_file(file_obj: Union[io.BytesIO, bytes, str]) -> pd.DataFrame:[cite: 1]
    """Load data from various file formats with optimized engines."""[cite: 1]
    try:[cite: 1]
        if isinstance(file_obj, (bytes, io.BytesIO)):[cite: 1]
            if isinstance(file_obj, bytes):[cite: 1]
                file_obj = io.BytesIO(file_obj)[cite: 1]
            [cite: 1]
            # Peek at extension from filename if available, else try multiple[cite: 1]
            name = getattr(file_obj, 'name', 'data.csv').lower()[cite: 1]
            ext = name.split(".")[-1] if "." in name else "csv"[cite: 1]
        else:[cite: 1]
            ext = file_obj.split(".")[-1].lower() if isinstance(file_obj, str) else "csv"[cite: 1]

        if ext == "csv":[cite: 1]
            data = pd.read_csv(file_obj, engine="pyarrow")[cite: 1]
        elif ext in ["xlsx", "xls"]:[cite: 1]
            data = pd.read_excel(file_obj, engine="openpyxl")[cite: 1]
        elif ext == "parquet":[cite: 1]
            data = pd.read_parquet(file_obj, engine="pyarrow")[cite: 1]
        else:[cite: 1]
            data = pd.read_json(file_obj)[cite: 1]

        return smart_clean_df(data)[cite: 1]
    except Exception as e:[cite: 1]
        raise ValueError(f"Data loading failed: {str(e)}")[cite: 1]


# ====================== VISUALIZATION ENGINE ======================

def generate_visualization([cite: 1]
    df: pd.DataFrame,[cite: 1]
    chart_type: str,[cite: 1]
    x_axis: str,[cite: 1]
    y_axis: Union[str, List[str]],[cite: 1]
    color_by: Optional[str] = None,[cite: 1]
    multi_y: bool = False,[cite: 1]
    max_rows: int = 50000[cite: 1]
) -> Dict[str, Any]:[cite: 1]
    """Generate Plotly figure with safe sampling."""[cite: 1]
    try:[cite: 1]
        if df is None or df.empty:[cite: 1]
            raise ValueError("Empty DataFrame")[cite: 1]

        # Safe sampling for large datasets[cite: 1]
        plot_df = df if len(df) <= max_rows else df.sample(max_rows, random_state=42)[cite: 1]
        warning = "Large dataset sampled to 50k points" if len(df) > max_rows else None[cite: 1]

        fig = None[cite: 1]
        args = {[cite: 1]
            "data_frame": plot_df,[cite: 1]
            "x": x_axis,[cite: 1]
            "template": "plotly_dark"[cite: 1]
        }[cite: 1]

        if multi_y and isinstance(y_axis, list):[cite: 1]
            args["y"] = y_axis[cite: 1]
        elif y_axis:[cite: 1]
            args["y"] = y_axis[cite: 1]

        if color_by:[cite: 1]
            args["color"] = color_by[cite: 1]

        if chart_type == "Bar":[cite: 1]
            fig = px.bar(**args)[cite: 1]
        elif chart_type == "Line":[cite: 1]
            fig = px.line(**args)[cite: 1]
        elif chart_type == "Scatter":[cite: 1]
            fig = px.scatter(**args)[cite: 1]
        elif chart_type == "Pie" and x_axis and y_axis:[cite: 1]
            fig = px.pie(plot_df, names=x_axis, values=y_axis)[cite: 1]
        elif chart_type == "Histogram":[cite: 1]
            fig = px.histogram(plot_df, x=y_axis if isinstance(y_axis, str) else y_axis[0], color=color_by)[cite: 1]
        elif chart_type == "Box Plot":[cite: 1]
            fig = px.box(**args)[cite: 1]
        elif chart_type == "Area Chart":[cite: 1]
            fig = px.area(**args)[cite: 1]

        if fig:[cite: 1]
            fig.update_layout([cite: 1]
                margin=dict(l=0, r=0, t=30, b=0),[cite: 1]
                hovermode="x unified"[cite: 1]
            )[cite: 1]
            
            # FIXED: Serialize figure to JSON string so it can travel over HTTP smoothly
            fig_json = pio.to_json(fig)
            
            return {
                "figure_json": fig_json,
                "sampled": warning is not None,[cite: 1]
                "sample_size": len(plot_df),[cite: 1]
                "success": True[cite: 1]
            }[cite: 1]
        else:[cite: 1]
            raise ValueError(f"Unsupported chart type: {chart_type}")[cite: 1]

    except Exception as e:[cite: 1]
        return {"success": False, "error": str(e), "figure_json": None}


# ====================== RAW ANALYTICS ======================

def get_raw_analytics(df: pd.DataFrame) -> Dict[str, Any]:[cite: 1]
    """Return dataset preview and descriptive statistics."""[cite: 1]
    try:[cite: 1]
        return {[cite: 1]
            "shape": df.shape,[cite: 1]
            "columns": df.columns.tolist(),[cite: 1]
            "numeric_columns": df.select_dtypes(include=np.number).columns.tolist(),[cite: 1]
            "head": df.head(5000).to_dict(orient="records"),[cite: 1]
            "describe": df.describe().to_dict(),[cite: 1]
            "missing_values": int(df.isnull().sum().sum()),[cite: 1]
            "success": True[cite: 1]
        }[cite: 1]
    except Exception as e:[cite: 1]
        return {"success": False, "error": str(e)}[cite: 1]


# ====================== ML & DATA OPERATIONS ======================

def encode_column(df: pd.DataFrame, column: str, encoding_type: str = "Label Encoding") -> Tuple[pd.DataFrame, Dict]:[cite: 1]
    """Apply encoding and return updated df + preview info."""[cite: 1]
    try:[cite: 1]
        df_copy = df.copy()[cite: 1]
        info = {}[cite: 1]

        if encoding_type == "Label Encoding":[cite: 1]
            le = LabelEncoder()[cite: 1]
            encoded_col = str(column) + "_encoded"[cite: 1]
            df_copy[encoded_col] = le.fit_transform(df_copy[column].astype(str))[cite: 1]
            info["encoded_column"] = encoded_col[cite: 1]
            info["classes"] = le.classes_.tolist()[cite: 1]

        elif encoding_type == "One-Hot Encoding":[cite: 1]
            df_copy = pd.get_dummies(df_copy, columns=[column], prefix=column)[cite: 1]
            info["one_hot_columns"] = [c for c in df_copy.columns if c.startswith(column)][cite: 1]

        return df_copy, {"success": True, "info": info}[cite: 1]

    except Exception as e:[cite: 1]
        return df, {"success": False, "error": str(e)}[cite: 1]


def edit_data(df: pd.DataFrame, operation: str, params: Dict) -> Tuple[pd.DataFrame, Dict]:[cite: 1]
    """Perform data edit operations (remove column/row, replace value)."""[cite: 1]
    try:[cite: 1]
        df_copy = df.copy()[cite: 1]
        result = {"success": True, "message": ""}[cite: 1]

        if operation == "Remove Column":[cite: 1]
            col = params.get("column")[cite: 1]
            if col in df_copy.columns:[cite: 1]
                df_copy.drop(columns=[col], inplace=True)[cite: 1]
                result["message"] = f"Column {col} removed"[cite: 1]
            else:[cite: 1]
                raise ValueError("Column not found")[cite: 1]

        elif operation == "Remove Row":[cite: 1]
            idx = int(params.get("index", 0))[cite: 1]
            if idx in df_copy.index:[cite: 1]
                df_copy.drop(index=idx, inplace=True)[cite: 1]
                result["message"] = f"Row {idx} removed"[cite: 1]
            else:[cite: 1]
                raise ValueError("Index not found")[cite: 1]

        elif operation == "Replace Value":[cite: 1]
            col = params.get("column")[cite: 1]
            idx = int(params.get("index"))[cite: 1]
            new_val = params.get("new_value")[cite: 1]
            if col in df_copy.columns and idx in df_copy.index:[cite: 1]
                df_copy.at[idx, col] = new_val[cite: 1]
                result["message"] = f"Value updated at [{idx}, {col}]"[cite: 1]
            else:[cite: 1]
                raise ValueError("Invalid index or column")[cite: 1]

        return df_copy, result[cite: 1]

    except Exception as e:[cite: 1]
        return df, {"success": False, "error": str(e)}[cite: 1]


def make_prediction([cite: 1]
    df: pd.DataFrame,[cite: 1]
    feature: str,[cite: 1]
    target: str,[cite: 1]
    model_type: str,[cite: 1]
    degree: int = 2,[cite: 1]
    predict_value: float = 0.0[cite: 1]
) -> Dict[str, Any]:[cite: 1]
    """Run Linear or Polynomial Regression prediction."""[cite: 1]
    try:[cite: 1]
        if feature not in df.columns or target not in df.columns:[cite: 1]
            raise ValueError("Feature or target column not found")[cite: 1]

        X = df[[feature]][cite: 1]
        y = df[target][cite: 1]

        if model_type == "Linear Regression":[cite: 1]
            model = LinearRegression()[cite: 1]
            model.fit(X, y)[cite: 1]
        elif model_type == "Polynomial Regression":[cite: 1]
            model = make_pipeline(PolynomialFeatures(degree), LinearRegression())[cite: 1]
            model.fit(X, y)[cite: 1]
        else:[cite: 1]
            raise ValueError("Unsupported model type")[cite: 1]

        prediction = model.predict([[predict_value]])[0][cite: 1]

        return {[cite: 1]
            "success": True,[cite: 1]
            "prediction": float(prediction),[cite: 1]
            "model_type": model_type,[cite: 1]
            "feature": feature,[cite: 1]
            "target": target[cite: 1]
        }[cite: 1]

    except Exception as e:[cite: 1]
        return {"success": False, "error": str(e)}[cite: 1]


# ====================== MAIN ORCHESTRATOR FOR WEB API ======================

def process_request(payload: Dict[str, Any]) -> Dict[str, Any]:[cite: 1]
    """
    FIXED UIFIED ENTRY POINT: Now fully supports network JSON strings.
    Converts network data payloads safely into Pandas DataFrames and outputs raw serializable JSON dicts.
    """
    try:
        operation = payload.get("operation")[cite: 1]
        raw_dataframe_data = payload.get("dataframe") 
        
        # Hydrate DataFrame from network JSON payload if available
        df = None
        if raw_dataframe_data is not None:
            df = payload_to_df(raw_dataframe_data)
        elif "file_data" in payload:[cite: 1]
            df = load_data_from_file(payload["file_data"])[cite: 1]

        if df is None or df.empty:[cite: 1]
            return {"success": False, "error": "No valid DataFrame provided or data parsing failed"}[cite: 1]

        if operation == "clean":[cite: 1]
            cleaned = smart_clean_df(df)[cite: 1]
            return {"success": True, "dataframe": df_to_payload(cleaned), "shape": cleaned.shape}

        elif operation == "visualize":[cite: 1]
            return generate_visualization([cite: 1]
                df,[cite: 1]
                chart_type=payload.get("chart_type"),[cite: 1]
                x_axis=payload.get("x_axis"),[cite: 1]
                y_axis=payload.get("y_axis"),[cite: 1]
                color_by=payload.get("color_by"),[cite: 1]
                multi_y=payload.get("multi_y", False)[cite: 1]
            )[cite: 1]

        elif operation == "analytics":[cite: 1]
            return get_raw_analytics(df)[cite: 1]

        elif operation == "encode":[cite: 1]
            updated_df, info = encode_column([cite: 1]
                df,[cite: 1]
                payload.get("column"),[cite: 1]
                payload.get("encoding_type", "Label Encoding")[cite: 1]
            )[cite: 1]
            return {"success": info["success"], "dataframe": df_to_payload(updated_df), **info}[cite: 1]

        elif operation == "edit":[cite: 1]
            updated_df, result = edit_data(df, payload.get("edit_op"), payload.get("params", {}))[cite: 1]
            return {"success": result["success"], "dataframe": df_to_payload(updated_df), **result}[cite: 1]

        elif operation == "predict":[cite: 1]
            return make_prediction([cite: 1]
                df,[cite: 1]
                feature=payload.get("feature"),[cite: 1]
                target=payload.get("target"),[cite: 1]
                model_type=payload.get("model_type"),[cite: 1]
                degree=payload.get("degree", 2),[cite: 1]
                predict_value=payload.get("predict_value", 0.0)[cite: 1]
            )[cite: 1]

        else:[cite: 1]
            return {"success": False, "error": f"Unknown operation: {operation}"}[cite: 1]

    except Exception as e:[cite: 1]
        return {"success": False, "error": f"Backend engine error: {str(e)}"}[cite: 1]


# ====================== STREAMLIT API ROUTING BRIDGE ======================
# This acts as a microservice listener. The frontend will trigger requests via URL parameters.

if "API_Gate" not in st.session_state:
    st.set_page_config(page_title="Graphico Core Engine", layout="wide")
    st.title("⚙️ Graphico Pro - Distributed Compute Backend Live")
    st.info("This system runs headless as an internal microservice engine.")

# Read query parameters or incoming session state mock triggers for testing
query_params = st.query_params

if "request_payload" in query_params:
    try:
        raw_payload = query_params["request_payload"]
        parsed_payload = json.loads(raw_payload)
        response_data = process_request(parsed_payload)
        st.json(response_data) # Streamlit returns JSON output directly onto the node screen
    except Exception as network_err:
        st.write({"success": False, "error": f"Network bridge serialization error: {network_err}"})
