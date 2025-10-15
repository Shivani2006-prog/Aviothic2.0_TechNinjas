# app/predict_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd
from typing import Optional

ARTIFACT_DIR = "app/model_artifacts"

# Load model and artifacts
model = joblib.load(f"{ARTIFACT_DIR}/seat_model.joblib")
ohe = joblib.load(f"{ARTIFACT_DIR}/ohe.joblib")
feature_info = joblib.load(f"{ARTIFACT_DIR}/feature_info.joblib")

app = FastAPI(title="Seat Availability Predictor")

class PredictRequest(BaseModel):
    train_id: str
    origin: str
    destination: str
    travel_date: str = Field(..., regex=r"^\d{4}-\d{2}-\d{2}$")  # YYYY-MM-DD
    booking_date: str = Field(..., regex=r"^\d{4}-\d{2}-\d{2}$")
    class_name: str
    seats_requested: Optional[int] = 1
    train_class_success: Optional[float] = None
    train_class_count: Optional[int] = None

def safe_ohe_transform(ohe, row, cat_cols):
    """Handle unseen categories safely by adding zeros for unknown categories"""
    row_cat = []
    for i, col in enumerate(cat_cols):
        val = row[col]
        if val in ohe.categories_[i]:
            row_cat.append([val])
        else:
            row_cat.append([None])  # Unknown category
    return ohe.transform(row_cat)

@app.post("/predict")
def predict(req: PredictRequest):
    try:
        travel_date = pd.to_datetime(req.travel_date)
        booking_date = pd.to_datetime(req.booking_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    days_to_departure = max((travel_date - booking_date).days, 0)
    train_class_success = req.train_class_success if req.train_class_success is not None else 0.5
    train_class_count = req.train_class_count if req.train_class_count is not None else 0

    row = {
        "train_id": req.train_id,
        "origin": req.origin,
        "destination": req.destination,
        "class": req.class_name,
        "days_to_departure": days_to_departure,
        "travel_month": str(travel_date.month),
        "travel_dow": str(travel_date.weekday()),
        "train_class_success": train_class_success,
        "train_class_count": train_class_count,
        "seats_requested": req.seats_requested
    }

    cat_cols = feature_info['cat_cols']
    num_cols = feature_info['num_cols']

    # Handle unseen categories
    X_cat = []
    for i, col in enumerate(cat_cols):
        val = row[col]
        # Map to None for unseen values
        if val not in ohe.categories_[i]:
            val = None
        X_cat.append(val)
    X_cat = ohe.transform([X_cat])
    
    X_num = np.array([[row[c] for c in num_cols]])
    X_all = np.hstack([X_cat, X_num])

    # Predict
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(X_all)[0][1]
    else:
        prob = float(model.predict(X_all)[0])
    
    predicted_label = int(prob >= 0.5)

    return {
        "probability_seat_available": round(float(prob), 4),
        "predicted_available": bool(predicted_label),
        "days_to_departure": days_to_departure
    }

@app.get("/")
def root():
    return {
        "status": "ok",
        "note": "POST to /predict with request body (train_id, origin, destination, travel_date, booking_date, class_name)"
    }
