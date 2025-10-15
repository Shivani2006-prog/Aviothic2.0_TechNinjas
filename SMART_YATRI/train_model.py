import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
import joblib
import os

# Paths
DATA_PATH = "data/train_bookings.csv"
ARTIFACT_DIR = "ml/model_artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# 1. Load data
df = pd.read_csv(DATA_PATH)

# Ensure expected columns exist
required_cols = ["train_id", "origin", "destination", "class", 
                 "travel_date", "booking_date", "seats_requested", "confirmed"]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing required column in dataset: {col}")

# 2. Feature engineering
df["travel_date"] = pd.to_datetime(df["travel_date"])
df["booking_date"] = pd.to_datetime(df["booking_date"])
df["days_to_departure"] = (df["travel_date"] - df["booking_date"]).dt.days.clip(lower=0)
df["travel_month"] = df["travel_date"].dt.month.astype(str)
df["travel_dow"] = df["travel_date"].dt.weekday.astype(str)

# Aggregate train-class historical success rate
agg = df.groupby(["train_id", "class"])["confirmed"].agg(["mean", "count"]).reset_index()
agg.rename(columns={"mean": "train_class_success", "count": "train_class_count"}, inplace=True)
df = df.merge(agg, on=["train_id", "class"], how="left")

# Features & target
cat_cols = ["train_id", "origin", "destination", "class", "travel_month", "travel_dow"]
num_cols = ["days_to_departure", "seats_requested", "train_class_success", "train_class_count"]

X_cat = df[cat_cols].astype(str)
X_num = df[num_cols]
y = df["confirmed"].astype(int)

# Encode categorical features
ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
X_cat_encoded = ohe.fit_transform(X_cat)

X_all = np.hstack([X_cat_encoded, X_num.values])

# 3. Train model
X_train, X_test, y_train, y_test = train_test_split(X_all, y, test_size=0.2, random_state=42)

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"✅ Model trained with accuracy: {score:.3f}")

# 4. Save artifacts
joblib.dump(model, f"{ARTIFACT_DIR}/seat_model.joblib")
joblib.dump(ohe, f"{ARTIFACT_DIR}/ohe.joblib")
joblib.dump({"cat_cols": cat_cols, "num_cols": num_cols}, f"{ARTIFACT_DIR}/feature_info.joblib")

print("📦 Artifacts saved in ml/model_artifacts/")

