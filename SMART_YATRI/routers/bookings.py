from fastapi import APIRouter, HTTPException, Query
from app.routes.prediction import PredictRequest
from datetime import datetime
import pandas as pd
import joblib
import os
from pathlib import Path

router = APIRouter(prefix="/booking", tags=["Booking"])

ARTIFACT_DIR = "ml/model_artifacts"
BOOKING_STORAGE = Path("data/bookings.csv")
ARCHIVE_DIR = Path("data/archive")

os.makedirs(ARCHIVE_DIR, exist_ok=True)

seat_model = joblib.load(os.path.join(ARTIFACT_DIR, "seat_model.joblib"))
seatleft_model = joblib.load(os.path.join(ARTIFACT_DIR, "seatleft_model.joblib"))
fare_model = joblib.load(os.path.join(ARTIFACT_DIR, "fare_model.joblib"))


# ---------- Utility: auto-archive ---------- #
def auto_archive():
    if not BOOKING_STORAGE.exists():
        return
    df = pd.read_csv(BOOKING_STORAGE)
    if df.empty:
        return
    today = datetime.now().date()
    past_or_cancelled = df[
        (pd.to_datetime(df["travel_date"]).dt.date < today) | (df["status"] == "cancelled")
    ]
    if not past_or_cancelled.empty:
        archive_path = ARCHIVE_DIR / f"archive_{today.strftime('%Y%m%d')}.csv"
        if archive_path.exists():
            old = pd.read_csv(archive_path)
            df_archive = pd.concat([old, past_or_cancelled], ignore_index=True)
        else:
            df_archive = past_or_cancelled
        df_archive.to_csv(archive_path, index=False)
        df.drop(past_or_cancelled.index).to_csv(BOOKING_STORAGE, index=False)


# ---------- Booking endpoints ---------- #
@router.post("/")
def book_ticket(request: PredictRequest):
    auto_archive()
    df = pd.DataFrame([request.dict(by_alias=True)])
    seat_available = int(seat_model.predict(df)[0])
    seats_left = int(seatleft_model.predict(df)[0])
    fare = round(float(fare_model.predict(df)[0]), 2)
    if seat_available == 0:
        return {"status": "rejected", "reason": "No seats available"}

    record = {
        "train_id": request.train_id,
        "origin": request.origin,
        "destination": request.destination,
        "travel_date": request.travel_date,
        "booking_date": request.booking_date,
        "class": request.class_name,
        "seats_requested": request.seats_requested,
        "fare": fare,
        "status": "confirmed",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if BOOKING_STORAGE.exists():
        existing = pd.read_csv(BOOKING_STORAGE)
        existing = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
    else:
        existing = pd.DataFrame([record])
    existing.to_csv(BOOKING_STORAGE, index=False)
    return {"status": "confirmed", "seats_left": seats_left, "fare": fare}


@router.get("/all")
def get_all_bookings():
    auto_archive()
    if not BOOKING_STORAGE.exists():
        return {"message": "No bookings found"}
    return pd.read_csv(BOOKING_STORAGE).to_dict(orient="records")


@router.delete("/cancel/{train_id}")
def cancel_booking(train_id: str):
    auto_archive()
    if not BOOKING_STORAGE.exists():
        raise HTTPException(status_code=404, detail="No bookings found")
    df = pd.read_csv(BOOKING_STORAGE)
    if train_id not in df["train_id"].values:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = df[df["train_id"] == train_id].iloc[-1]
    travel_date = datetime.strptime(booking["travel_date"], "%Y-%m-%d")
    days_left = (travel_date - datetime.now()).days
    fare = booking["fare"]
    if days_left > 4:
        refund = fare * 0.9
    elif 1 <= days_left <= 4:
        refund = fare * 0.5
    else:
        refund = fare * 0.1
    df.loc[df["train_id"] == train_id, "status"] = "cancelled"
    df.to_csv(BOOKING_STORAGE, index=False)
    auto_archive()
    return {
        "status": "cancelled",
        "train_id": train_id,
        "refund_amount": round(refund, 2),
        "message": "Booking cancelled successfully and archived",
    }


@router.get("/status/{train_id}")
def get_booking_status(train_id: str):
    auto_archive()
    if not BOOKING_STORAGE.exists():
        raise HTTPException(status_code=404, detail="No bookings found")
    df = pd.read_csv(BOOKING_STORAGE)
    if train_id not in df["train_id"].values:
        raise HTTPException(status_code=404, detail="No booking found")
    booking = df[df["train_id"] == train_id].iloc[-1]
    return {
        "train_id": booking["train_id"],
        "status": booking["status"],
        "fare": booking["fare"],
        "timestamp": booking["timestamp"],
    }


@router.get("/search")
def search_bookings(
    origin: str | None = Query(None),
    destination: str | None = Query(None),
    status: str | None = Query(None),
    class_name: str | None = Query(None, alias="class"),
    travel_date: str | None = Query(None),
):
    auto_archive()
    if not BOOKING_STORAGE.exists():
        return {"message": "No bookings found"}
    df = pd.read_csv(BOOKING_STORAGE)
    if origin:
        df = df[df["origin"].str.upper() == origin.upper()]
    if destination:
        df = df[df["destination"].str.upper() == destination.upper()]
    if status:
        df = df[df["status"].str.lower() == status.lower()]
    if class_name:
        df = df[df["class"].str.upper() == class_name.upper()]
    if travel_date:
        df = df[df["travel_date"] == travel_date]
    if df.empty:
        return {"message": "No matching bookings found"}
    return df.to_dict(orient="records")


@router.get("/archive")
def view_archived_bookings(date: str | None = Query(None)):
    auto_archive()
    if not os.listdir(ARCHIVE_DIR):
        return {"message": "No archived records found"}
    if date:
        file = ARCHIVE_DIR / f"archive_{date}.csv"
        if not file.exists():
            raise HTTPException(status_code=404, detail="Archive not found for given date")
        df = pd.read_csv(file)
        return {"archive_date": date, "records": df.to_dict(orient="records")}
    all_records = []
    for file in ARCHIVE_DIR.glob("archive_*.csv"):
        df = pd.read_csv(file)
        all_records.extend(df.to_dict(orient="records"))
    return {"total_archived_records": len(all_records), "records": all_records}


# ---------- NEW: Dashboard Summary ---------- #
@router.get("/summary")
def booking_summary():
    """Return a summary dashboard of all bookings and revenue/refund stats."""
    auto_archive()

    total_confirmed = total_cancelled = total_archived = 0
    total_revenue = total_refund = 0.0

    # Active file
    if BOOKING_STORAGE.exists():
        df = pd.read_csv(BOOKING_STORAGE)
        total_confirmed = (df["status"] == "confirmed").sum()
        total_cancelled = (df["status"] == "cancelled").sum()
        total_revenue = df[df["status"] == "confirmed"]["fare"].sum()

    # Archived data
    if os.listdir(ARCHIVE_DIR):
        for file in ARCHIVE_DIR.glob("archive_*.csv"):
            df = pd.read_csv(file)
            total_archived += len(df)
            total_refund += df[df["status"] == "cancelled"]["fare"].sum()

    chart_data = {
        "labels": ["Confirmed", "Cancelled", "Archived"],
        "values": [total_confirmed, total_cancelled, total_archived],
    }

    return {
        "summary": {
            "total_confirmed": int(total_confirmed),
            "total_cancelled": int(total_cancelled),
            "total_archived": int(total_archived),
            "total_revenue": round(total_revenue, 2),
            "total_refund": round(total_refund, 2),
        },
        "chart_data": chart_data,
    }
