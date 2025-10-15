"""
Smart Yatri Pydantic Schemas
Author: Abhay Tripathi
Project: Smart Yatri
Description: Request validation and response models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# ----------------------
# Booking Schemas
# ----------------------
class BookingCreate(BaseModel):
    """
    Schema for creating a new booking
    """
    user_id: int
    train_id: str
    origin: str
    destination: str
    travel_date: date
    booking_date: date
    class_name: str = Field(..., alias="class")
    seats_booked: int = Field(..., gt=0)
    fare: float = Field(..., gt=0)


class BookingResponse(BaseModel):
    """
    Schema for returning booking details
    """
    id: int
    user_id: int
    train_id: str
    origin: str
    destination: str
    travel_date: date
    booking_date: date
    class_name: str
    seats_booked: int
    fare: float
    status: str
    cancellation_time: Optional[datetime] = None

    class Config:
        orm_mode = True  # allow reading from SQLAlchemy models


class CancelResponse(BaseModel):
    """
    Schema for returning cancellation details
    """
    id: int
    status: str
    cancellation_time: Optional[datetime] = None


# ----------------------
# Seat Prediction Schemas
# ----------------------
class SeatAvailabilityResponse(BaseModel):
    """
    Schema for seat availability prediction
    """
    train_id: str
    class_name: str
    travel_date: date
    probability_available: float  # 0.0 to 1.0


# ----------------------
# Fare Trends Schemas
# ----------------------
class FareTrendPoint(BaseModel):
    """
    Schema for a single fare trend data point
    """
    date: date
    avg_fare: float


class FareTrendsResponse(BaseModel):
    """
    Schema for dynamic fare trends
    """
    booked_trends: List[FareTrendPoint] = []
    predicted_trends: List[FareTrendPoint] = []  # placeholder for future ML predictions
