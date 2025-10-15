"""
Booking-related endpoints:
- POST /bookings/               -> create a booking
- GET  /bookings/{user_id}      -> user-specific booking history
- GET  /bookings/summary        -> admin booking summary (all bookings)
- PUT  /bookings/{booking_id}/cancel -> soft-cancel a booking (IRCTC-style)
- GET  /fare-trends/{user_id}   -> fare trends (booked fares + predicted placeholder)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta, date

from app.database import get_db
from app.models import Booking
from app.schemas import BookingCreate, BookingResponse, CancelResponse, FareTrendsResponse, FareTrendPoint

# Router prefixed with /bookings
router = APIRouter(prefix="/bookings", tags=["Booking"])

@router.post("/", response_model=BookingResponse)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    """
    Create and persist a booking.
    """
    bk = Booking(
        user_id=payload.user_id,
        train_id=payload.train_id,
        origin=payload.origin,
        destination=payload.destination,
        travel_date=payload.travel_date,
        booking_date=payload.booking_date,
        class_name=payload.class_name,
        seats_booked=payload.seats_booked,
        fare=payload.fare,
        status="CONFIRMED"
    )
    db.add(bk)
    db.commit()
    db.refresh(bk)
    return bk

@router.get("/{user_id}", response_model=List[BookingResponse])
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all bookings for given user (includes cancelled records).
    """
    bookings = db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.travel_date.desc()).all()
    return bookings

@router.get("/summary", response_model=List[BookingResponse])
def get_all_bookings_summary(limit: Optional[int] = Query(100, gt=0), db: Session = Depends(get_db)):
    """
    Admin/Staff endpoint that returns booking summary (all users).
    Default limit is 100 records unless specified.
    """
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(limit).all()
    return bookings

@router.put("/{booking_id}/cancel", response_model=CancelResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Soft-cancel a booking. Sets status = CANCELLED and records cancellation_time.
    (No hard-delete to preserve history.)
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == "CANCELLED":
        return CancelResponse(id=booking.id, status=booking.status, cancellation_time=booking.cancellation_time)

    # Implementing a simple cancellation timestamp and marking status
    booking.status = "CANCELLED"
    booking.cancellation_time = datetime.utcnow()
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return CancelResponse(id=booking.id, status=booking.status, cancellation_time=booking.cancellation_time)

@router.get("/fare-trends/{user_id}", response_model=FareTrendsResponse)
def fare_trends(
    user_id: int,
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    days: int = Query(30, gt=0),
    db: Session = Depends(get_db)
):
    """
    Produce fare trends for a given user:
    - booked_trends: aggregated average fare from past bookings (filtered)
    - predicted_trends: placeholder list that can be replaced by ML output later
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)

    q = db.query(func.date(Booking.booking_date).label("date"), func.avg(Booking.fare).label("avg_fare"))\
          .filter(Booking.user_id == user_id)\
          .filter(Booking.booking_date >= start_date)\
          .filter(Booking.booking_date <= end_date)

    if origin:
        q = q.filter(Booking.origin == origin)
    if destination:
        q = q.filter(Booking.destination == destination)

    q = q.group_by(func.date(Booking.booking_date)).order_by(func.date(Booking.booking_date))
    rows = q.all()

    booked_trends = [FareTrendPoint(date=r.date, avg_fare=float(r.avg_fare)) for r in rows]

    # Predicted trends: placeholder. Replace with actual ML calls later.
    predicted_trends = []
    # Example placeholder: predict next 7 days using model (to be integrated)
    for i in range(1, 8):
        future_date = end_date + timedelta(days=i)
        predicted_trends.append({"date": future_date.isoformat(), "predicted_fare": None})

    return FareTrendsResponse(booked_trends=booked_trends, predicted_trends=predicted_trends)
