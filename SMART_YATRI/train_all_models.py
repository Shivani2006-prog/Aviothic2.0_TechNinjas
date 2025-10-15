import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error

# ✅ CSV is in the same folder as the script
DATA_PATH = "train bookings.csv"
ARTIFACT_DIR = "ml/model_artifacts"

os.makedirs(ARTIFACT_DIR, exist_ok=True)

TOTAL_SEATS = {"SL": 72, "3A": 64, "2A": 48}
RANDOM_STATE = 42
TEST_SIZE = 0.2


def parse_dates(df):
    for col in ["travel_date", "booking_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def add_engineered_features(df):
    if "travel_date" in df.columns and "booking_date" in df.columns:
        df["lead_time_days"] = (df["travel_date"] - df["booking_date"]).dt.days
        df["lead_time_days"] = df["lead_time_days"].fillna(-1).astype(int)
    else:
        df["lead_time_days"] = -1

    if "travel_date" in df.columns:
        df["travel_dow"] = df["travel_date"].dt.weekday.fillna(-1).astype(int)
    else:
        df["travel_dow"] = -1

    if "seats_requested" in df.columns:
        df["seats_requested"] = pd.to_numeric(
            df["seats_requested"], errors="coerce"
        ).fillna(1).astype(int)
    else:
        df["seats_requested"] = 1

    def est_distance(o, d):
        if pd.isna(o) or pd.isna(d):
            return 100
        return abs(sum(map(ord, str(o))) - sum(map(ord, str(d)))) % 1200 + 50

    df["est_distance_km"] = df.apply(
        lambda r: est_distance(r.get("origin"), r.get("destination")), axis=1
    )

    df["total_seats_for_class"] = (
        df.get("class", "").map(TOTAL_SEATS).fillna(72).astype(int)
    )

    df["seats_left"] = (
        df["total_seats_for_class"] - df["seats_requested"]
    ).clip(lower=0)

    class_base = {"SL": 200, "3A": 800, "2A": 1500}
    df["class_base"] = df.get("class", "").map(class_base).fillna(300)

    df["days_to_travel"] = df["lead_time_days"].apply(lambda x: max(x, 0))
    df["fare_synthetic"] = (
        df["class_base"]
        + (df["est_distance_km"] * 0.5)
        - (df["days_to_travel"] * 0.5)
        + np.random.normal(scale=10, size=len(df))
    ).clip(lower=50)

    return df


def build_and_train_classification(df):
    features = [
        "train_id", "origin", "destination", "class",
        "lead_time_days", "travel_dow", "seats_requested"
    ]
    X = df[features]
    y = df["booked"].fillna(0).astype(int)

    categorical_cols = ["train_id", "origin", "destination", "class"]
    numeric_cols = ["lead_time_days", "travel_dow", "seats_requested"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols)
        ]
    )

    clf = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestClassifier(random_state=RANDOM_STATE))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)

    joblib.dump(clf, os.path.join(ARTIFACT_DIR, "seat_model.joblib"))
    print(f"✅ Seat availability model saved (Accuracy: {acc:.3f})")


def build_and_train_seatleft(df):
    features = [
        "train_id", "origin", "destination", "class",
        "lead_time_days", "travel_dow", "seats_requested"
    ]
    X = df[features]
    y = df["seats_left"]

    categorical_cols = ["train_id", "origin", "destination", "class"]
    numeric_cols = ["lead_time_days", "travel_dow", "seats_requested"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols),
        ]
    )

    reg = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(random_state=RANDOM_STATE))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    reg.fit(X_train, y_train)
    preds = reg.predict(X_test)
    mse = mean_squared_error(y_test, preds)

    joblib.dump(reg, os.path.join(ARTIFACT_DIR, "seatleft_model.joblib"))
    print(f"✅ Seats-left model saved (MSE: {mse:.3f})")


def build_and_train_fare(df):
    features = [
        "train_id", "origin", "destination", "class",
        "lead_time_days", "travel_dow", "seats_requested", "est_distance_km"
    ]
    X = df[features]
    y = df["fare_synthetic"]

    categorical_cols = ["train_id", "origin", "destination", "class"]
    numeric_cols = ["lead_time_days", "travel_dow", "seats_requested", "est_distance_km"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols),
        ]
    )

    reg = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(random_state=RANDOM_STATE))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    reg.fit(X_train, y_train)
    preds = reg.predict(X_test)
    mse = mean_squared_error(y_test, preds)

    joblib.dump(reg, os.path.join(ARTIFACT_DIR, "fare_model.joblib"))
    print(f"✅ Fare model saved (MSE: {mse:.3f})")


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"❌ Dataset not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df = parse_dates(df)
    df = add_engineered_features(df)

    build_and_train_classification(df)
    build_and_train_seatleft(df)
    build_and_train_fare(df)

    print("\n🎉 All models trained and saved to:", ARTIFACT_DIR)


if __name__ == "__main__":
    main()
