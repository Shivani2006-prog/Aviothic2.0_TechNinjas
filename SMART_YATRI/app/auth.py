from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app import models, database

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def authenticate_admin(form_data: OAuth2PasswordRequestForm, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or user.password != form_data.password or not user.is_admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": user.username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return token


from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Admins only!")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
