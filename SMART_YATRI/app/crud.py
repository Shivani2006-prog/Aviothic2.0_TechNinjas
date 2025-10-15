"""
Smart Yatri CRUD operations
Author: Abhay Tripathi
Project: Smart Yatri
"""
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta
import random

# -----------------------------
# Booking Operations
# -----------------------------
def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_all_bookings(db: Session):
    return db.query(models.Booking).all()

def cancel_booking(db: Session, booking_id: int):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        return None
    booking.status = "cancelled"
    booking.cancellation_time = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking

# -----------------------------
# Prediction & Fare Trends
# -----------------------------
def predict_seat_availability(train_id: str, class_name: str, travel_date: datetime):
    # Human-like pseudo prediction
    probability = random.uniform(0.3, 0.95)
    return {"train_id": train_id, "class_name": class_name, "travel_date": travel_date, "probability_available": round(probability, 2)}

def get_fare_trends(train_id: str, class_name: str):
    today = datetime.today().date()
    booked_trends = [{"date": today - timedelta(days=i), "avg_fare": random.randint(500, 1500)} for i in range(7)]
    predicted_trends = [{"date": today + timedelta(days=i), "avg_fare": random.randint(600, 1600)} for i in range(7)]
    return {"booked_trends": booked_trends, "predicted_trends": predicted_trends}
