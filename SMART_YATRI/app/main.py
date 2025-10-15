"""
Smart Yatri FastAPI Main Application
Author: Abhay Tripathi
Project: Smart Yatri
Description: Main API routes for train bookings, cancellations, and seat/fare predictions.
"""

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List

from app import models, schemas
from app.database import engine, Base, get_db

# ----------------------
# Initialize database tables
# ----------------------
Base.metadata.create_all(bind=engine)

# ----------------------
# FastAPI instance
# ----------------------
app = FastAPI(
    title="Smart Yatri API",
    description="API for train bookings, cancellations, and predictions",
    version="1.0.0"
)

# ----------------------
# Routes
# ----------------------

@app.post("/bookings/", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    """
    Create a new train booking
    """
    db_booking = models.Booking(
        user_id=booking.user_id,
        train_id=booking.train_id,
        origin=booking.origin,
        destination=booking.destination,
        travel_date=booking.travel_date,
        booking_date=booking.booking_date,
        class_name=booking.class_name,
        seats_booked=booking.seats_booked,
        fare=booking.fare,
        status="confirmed"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


@app.get("/bookings/", response_model=List[schemas.BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    """
    Fetch all bookings
    """
    bookings = db.query(models.Booking).all()
    return bookings


@app.get("/bookings/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single booking by ID
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@app.post("/bookings/{booking_id}/cancel", response_model=schemas.CancelResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Cancel a booking by ID
    """
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status == "canceled":
        raise HTTPException(status_code=400, detail="Booking already canceled")

    booking.status = "canceled"
    booking.cancellation_time = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@app.get("/seat-availability/", response_model=List[schemas.SeatAvailabilityResponse])
def check_seat_availability(train_id: str, class_name: str, travel_date: date, db: Session = Depends(get_db)):
    """
    Check seat availability probability for a train class on a given date
    """
    # Example logic: returning static probability (replace with ML or DB logic)
    probability = 0.75
    return [
        schemas.SeatAvailabilityResponse(
            train_id=train_id,
            class_name=class_name,
            travel_date=travel_date,
            probability_available=probability
        )
    ]


@app.get("/fare-trends/", response_model=schemas.FareTrendsResponse)
def get_fare_trends(train_id: str, class_name: str, db: Session = Depends(get_db)):
    """
    Get past and predicted fare trends for a train class
    """
    # Example data (replace with ML or DB logic)
    booked_trends = [
        schemas.FareTrendPoint(date=date.today(), avg_fare=100.0),
        schemas.FareTrendPoint(date=date.today(), avg_fare=105.0),
    ]
    predicted_trends = [
        schemas.FareTrendPoint(date=date.today(), avg_fare=110.0),
        schemas.FareTrendPoint(date=date.today(), avg_fare=115.0),
    ]
    return schemas.FareTrendsResponse(
        booked_trends=booked_trends,
        predicted_trends=predicted_trends
    )
