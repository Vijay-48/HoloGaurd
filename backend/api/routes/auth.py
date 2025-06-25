from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import crud, security
from api.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, username):
        raise HTTPException(400, "User exists")
    user = crud.create_user(db, username, password)
    return {"username": user.username}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Bad credentials")
    token = security.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
