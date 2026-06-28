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
px.defaults.template = "plotly_dark"

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

def img_to_base64(image_path: str) -> str:
    """Convert image to base64 (kept for potential internal use)."""
    try:
        img_bytes = Path(image_path).read_bytes()
        encoded = base64.b64encode(img_bytes).decode("utf-8")
        ext = image_path.lower().split(".")[-1]
        mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
        return f"data:image/{mime};base64,{encoded}"
    except Exception:
        return ""


def smart_clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """BRAHMASTRA: Core data cleaning with memory optimization."""
    if df is None or df.empty:
        return df

    # Downcast numeric types to save RAM
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
                    df_clean[column] = df_clean[column].fillna(
                        mean_val if pd.notnull(mean_val) else 0
                    )
                else:
                    mode_vals = df_clean[column].mode()
                    df_clean[column] = df_clean[column].fillna(
                        mode_vals[0] if not mode_vals.empty else "Unknown"
                    )
    return df_clean


# ====================== DATA LOADING ======================

def load_data_from_file(file_obj: Union[io.BytesIO, bytes, str]) -> pd.DataFrame:
    """Load data from various file formats with optimized engines."""
    try:
        if isinstance(file_obj, (bytes, io.BytesIO)):
            if isinstance(file_obj, bytes):
                file_obj = io.BytesIO(file_obj)
           
            # Peek at extension from filename if available, else try multiple
            name = getattr(file_obj, 'name', 'data.csv').lower()
            ext = name.split(".")[-1] if "." in name else "csv"
        else:
            ext = file_obj.split(".")[-1].lower() if isinstance(file_obj, str) else "csv"

        if ext == "csv":
            data = pd.read_csv(file_obj, engine="pyarrow")
        elif ext in ["xlsx", "xls"]:
            data = pd.read_excel(file_obj, engine="openpyxl")
        elif ext == "parquet":
            data = pd.read_parquet(file_obj, engine="pyarrow")
        else:
            data = pd.read_json(file_obj)

        return smart_clean_df(data)
    except Exception as e:
        raise ValueError(f"Data loading failed: {str(e)}")


# ====================== VISUALIZATION ENGINE ======================

def generate_visualization(
    df: pd.DataFrame,
    chart_type: str,
    x_axis: str,
    y_axis: Union[str, List[str]],
    color_by: Optional[str] = None,
    multi_y: bool = False,
    max_rows: int = 50000
) -> Dict[str, Any]:
    """Generate Plotly figure with safe sampling."""
    try:
        if df is None or df.empty:
            raise ValueError("Empty DataFrame")

        # Safe sampling for large datasets
        plot_df = df if len(df) <= max_rows else df.sample(max_rows, random_state=42)
        warning = "Large dataset sampled to 50k points" if len(df) > max_rows else None

        fig = None
        args = {
            "data_frame": plot_df,
            "x": x_axis,
            "template": "plotly_dark"
        }

        if multi_y and isinstance(y_axis, list):
            args["y"] = y_axis
        elif y_axis:
            args["y"] = y_axis

        if color_by:
            args["color"] = color_by

        if chart_type == "Bar":
            fig = px.bar(**args)
        elif chart_type == "Line":
            fig = px.line(**args)
        elif chart_type == "Scatter":
            fig = px.scatter(**args)
        elif chart_type == "Pie" and x_axis and y_axis:
            fig = px.pie(plot_df, names=x_axis, values=y_axis)
        elif chart_type == "Histogram":
            fig = px.histogram(plot_df, x=y_axis if isinstance(y_axis, str) else y_axis[0], color=color_by)
        elif chart_type == "Box Plot":
            fig = px.box(**args)
        elif chart_type == "Area Chart":
            fig = px.area(**args)

        if fig:
            fig.update_layout(
                margin=dict(l=0, r=0, t=30, b=0),
                hovermode="x unified"
            )
            
            # Serialize figure to JSON string so it can travel over HTTP smoothly
            fig_json = pio.to_json(fig)
            
            return {
                "figure_json": fig_json,
                "sampled": warning is not None,
                "sample_size": len(plot_df),
                "success": True
            }
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

    except Exception as e:
        return {"success": False, "error": str(e), "figure_json": None}


# ====================== RAW ANALYTICS ======================

def get_raw_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """Return dataset preview and descriptive statistics."""
    try:
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "numeric_columns": df.select_dtypes(include=np.number).columns.tolist(),
            "head": df.head(5000).to_dict(orient="records"),
            "describe": df.describe().to_dict(),
            "missing_values": int(df.isnull().sum().sum()),
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ====================== ML & DATA OPERATIONS ======================

def encode_column(df: pd.DataFrame, column: str, encoding_type: str = "Label Encoding") -> Tuple[pd.DataFrame, Dict]:
    """Apply encoding and return updated df + preview info."""
    try:
        df_copy = df.copy()
        info = {}

        if encoding_type == "Label Encoding":
            le = LabelEncoder()
            encoded_col = str(column) + "_encoded"
            df_copy[encoded_col] = le.fit_transform(df_copy[column].astype(str))
            info["encoded_column"] = encoded_col
            info["classes"] = le.classes_.tolist()

        elif encoding_type == "One-Hot Encoding":
            df_copy = pd.get_dummies(df_copy, columns=[column], prefix=column)
            info["one_hot_columns"] = [c for c in df_copy.columns if c.startswith(column)]

        return df_copy, {"success": True, "info": info}

    except Exception as e:
        return df, {"success": False, "error": str(e)}


def edit_data(df: pd.DataFrame, operation: str, params: Dict) -> Tuple[pd.DataFrame, Dict]:
    """Perform data edit operations (remove column/row, replace value)."""
    try:
        df_copy = df.copy()
        result = {"success": True, "message": ""}

        if operation == "Remove Column":
            col = params.get("column")
            if col in df_copy.columns:
                df_copy.drop(columns=[col], inplace=True)
                result["message"] = f"Column {col} removed"
            else:
                raise ValueError("Column not found")

        elif operation == "Remove Row":
            idx = int(params.get("index", 0))
            if idx in df_copy.index:
                df_copy.drop(index=idx, inplace=True)
                result["message"] = f"Row {idx} removed"
            else:
                raise ValueError("Index not found")

        elif operation == "Replace Value":
            col = params.get("column")
            idx = int(params.get("index"))
            new_val = params.get("new_value")
            if col in df_copy.columns and idx in df_copy.index:
                df_copy.at[idx, col] = new_val
                result["message"] = f"Value updated at [{idx}, {col}]"
            else:
                raise ValueError("Invalid index or column")

        return df_copy, result

    except Exception as e:
        return df, {"success": False, "error": str(e)}


def make_prediction(
    df: pd.DataFrame,
    feature: str,
    target: str,
    model_type: str,
    degree: int = 2,
    predict_value: float = 0.0
) -> Dict[str, Any]:
    """Run Linear or Polynomial Regression prediction."""
    try:
        if feature not in df.columns or target not in df.columns:
            raise ValueError("Feature or target column not found")

        X = df[[feature]]
        y = df[target]

        if model_type == "Linear Regression":
            model = LinearRegression()
            model.fit(X, y)
        elif model_type == "Polynomial Regression":
            model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
            model.fit(X, y)
        else:
            raise ValueError("Unsupported model type")

        prediction = model.predict([[predict_value]])[0]

        return {
            "success": True,
            "prediction": float(prediction),
            "model_type": model_type,
            "feature": feature,
            "target": target
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ====================== MAIN ORCHESTRATOR FOR WEB API ======================

def process_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    FIXED UNIFIED ENTRY POINT: Now fully supports network JSON strings.
    Converts network data payloads safely into Pandas DataFrames and outputs raw serializable JSON dicts.
    """
    try:
        operation = payload.get("operation")
        raw_dataframe_data = payload.get("dataframe") 
        
        # Hydrate DataFrame from network JSON payload if available
        df = None
        if raw_dataframe_data is not None:
            df = payload_to_df(raw_dataframe_data)
        elif "file_data" in payload:
            df = load_data_from_file(payload["file_data"])

        if df is None or df.empty:
            return {"success": False, "error": "No valid DataFrame provided or data parsing failed"}

        if operation == "clean":
            cleaned = smart_clean_df(df)
            return {"success": True, "dataframe": df_to_payload(cleaned), "shape": cleaned.shape}

        elif operation == "visualize":
            return generate_visualization(
                df,
                chart_type=payload.get("chart_type"),
                x_axis=payload.get("x_axis"),
                y_axis=payload.get("y_axis"),
                color_by=payload.get("color_by"),
                multi_y=payload.get("multi_y", False)
            )

        elif operation == "analytics":
            return get_raw_analytics(df)

        elif operation == "encode":
            updated_df, info = encode_column(
                df,
                payload.get("column"),
                payload.get("encoding_type", "Label Encoding")
            )
            return {"success": info["success"], "dataframe": df_to_payload(updated_df), **info}

        elif operation == "edit":
            updated_df, result = edit_data(df, payload.get("edit_op"), payload.get("params", {}))
            return {"success": result["success"], "dataframe": df_to_payload(updated_df), **result}

        elif operation == "predict":
            return make_prediction(
                df,
                feature=payload.get("feature"),
                target=payload.get("target"),
                model_type=payload.get("model_type"),
                degree=payload.get("degree", 2),
                predict_value=payload.get("predict_value", 0.0)
            )

        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

    except Exception as e:
        return {"success": False, "error": f"Backend engine error: {str(e)}"}


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
