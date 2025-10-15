from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import joblib
import pandas as pd
import os

router = APIRouter(prefix="/predict", tags=["Prediction"])

ARTIFACT_DIR = "ml/model_artifacts"

seat_model = joblib.load(os.path.join(ARTIFACT_DIR, "seat_model.joblib"))
seatleft_model = joblib.load(os.path.join(ARTIFACT_DIR, "seatleft_model.joblib"))
fare_model = joblib.load(os.path.join(ARTIFACT_DIR, "fare_model.joblib"))

class PredictRequest(BaseModel):
    train_id: str
    origin: str
    destination: str
    travel_date: str
    booking_date: str
    class_name: str = Field(..., alias="class")
    seats_requested: int = Field(..., gt=0)

    @field_validator("travel_date", "booking_date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in format YYYY-MM-DD")
        return value

@router.post("/")
def predict(request: PredictRequest):
    df = pd.DataFrame([{
        "train_id": request.train_id,
        "origin": request.origin,
        "destination": request.destination,
        "travel_date": request.travel_date,
        "booking_date": request.booking_date,
        "class": request.class_name,
        "seats_requested": request.seats_requested,
    }])
    seat_available = int(seat_model.predict(df)[0])
    seats_left = int(seatleft_model.predict(df)[0])
    predicted_fare = round(float(fare_model.predict(df)[0]), 2)
    return {
        "seat_available": seat_available,
        "seats_left": seats_left,
        "predicted_fare": predicted_fare
    }
