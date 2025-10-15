"""
Smart Yatri Database Models
Author: Abhay Tripathi
Project: Smart Yatri
Description: SQLAlchemy models for bookings
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    train_id = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    travel_date = Column(Date, nullable=False)
    booking_date = Column(Date, nullable=False)
    class_name = Column(String, nullable=False)
    seats_booked = Column(Integer, nullable=False)
    fare = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="CONFIRMED")
    cancellation_time = Column(DateTime, nullable=True, default=None)
