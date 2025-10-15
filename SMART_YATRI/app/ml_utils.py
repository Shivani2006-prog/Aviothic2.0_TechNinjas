DEFAULT_CSV = "data/default_dataset.csv"
UPLOADS_DIR = "uploads"
UPLOAD_FILE_NAME = "latest.csv"

def train_from_csv(csv_path: str):
    return {"csv_used": csv_path, "status": "model trained"}

def predict_from_input(train_id, class_name, month, days_to_departure, demand_index):
    return 0.7  # Dummy fixed probability
