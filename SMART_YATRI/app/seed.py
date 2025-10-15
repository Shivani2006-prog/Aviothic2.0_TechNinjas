from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app import models


def seed():
    db: Session = SessionLocal()

    # Ensure tables exist
    init_db()

    # Seed Users
    if db.query(models.User).count() == 0:
        users = [
            models.User(username="admin", password="admin123", is_admin=True),
            models.User(username="user1", password="password1"),
            models.User(username="user2", password="password2"),
        ]
        db.add_all(users)
        db.commit()
        print("✅ Users inserted")

    # Seed Trains
    if db.query(models.Train).count() == 0:
        trains = [
            models.Train(id="T001", name="Express A", origin="Delhi", destination="Mumbai", total_seats=300),
            models.Train(id="T002", name="Express B", origin="Kolkata", destination="Chennai", total_seats=250),
        ]
        db.add_all(trains)
        db.commit()
        print("✅ Trains inserted")

    # Seed Bookings
    if db.query(models.Booking).count() == 0:
        bookings = [
            models.Booking(user_id=1, train_id="T001", travel_date=date(2025, 10, 20),
                           class_type="Sleeper", seats_booked=2, price=1500.0),
            models.Booking(user_id=2, train_id="T002", travel_date=date(2025, 10, 25),
                           class_type="AC", seats_booked=1, price=2000.0),
        ]
        db.add_all(bookings)
        db.commit()
        print("✅ Bookings inserted")

    db.close()


if __name__ == "__main__":
    seed()
    print("🎉 Seeding completed successfully")
