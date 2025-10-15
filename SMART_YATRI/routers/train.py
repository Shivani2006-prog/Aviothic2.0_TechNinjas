from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/trains", tags=["Trains"])


@router.post("/", response_model=schemas.TrainOut)
def add_train(train: schemas.TrainCreate, db: Session = Depends(get_db)):
    return crud.create_train(db, train)


@router.get("/", response_model=list[schemas.TrainOut])
def list_trains(db: Session = Depends(get_db)):
    return crud.get_trains(db)


@router.delete("/{train_id}")
def delete_train(train_id: int, db: Session = Depends(get_db)):
    success = crud.delete_train(db, train_id)
    if not success:
        raise HTTPException(status_code=404, detail="Train not found")
    return {"message": "Train deleted"}
