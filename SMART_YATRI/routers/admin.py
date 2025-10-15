import os, shutil
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.auth import get_current_admin, oauth2_scheme
from app.ml_utils import train_from_csv, DEFAULT_CSV, UPLOADS_DIR, UPLOAD_FILE_NAME

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/upload-retrain")
def upload_and_retrain(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    _ = get_current_admin(token)

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    save_path = os.path.join(UPLOADS_DIR, UPLOAD_FILE_NAME)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.close()

    status = train_from_csv(save_path)
    return {"status": "trained", "details": status}

@router.post("/retrain-default")
def retrain_default(token: str = Depends(oauth2_scheme)):
    _ = get_current_admin(token)
    if not os.path.exists(DEFAULT_CSV):
        raise HTTPException(status_code=400, detail=f"No dataset found at {DEFAULT_CSV}")
    status = train_from_csv(DEFAULT_CSV)
    return {"status": "trained", "details": status}
