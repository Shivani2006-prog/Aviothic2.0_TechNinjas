from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/trains", tags=["Trains"])

@router.post("/", response_model=schemas.TrainOut)
def create_train(train: schemas.TrainCreate, db: Session = Depends(get_db)):
    return crud.create_train(db, train.dict())

@router.get("/", response_model=List[schemas.TrainOut])
def list_trains(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_trains(db, skip, limit)
