from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.deps import get_db, get_user
from auth import crud

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/")
def read_history(db: Session = Depends(get_db), user = Depends(get_user)):
    records = crud.get_history_for_user(db, user.id)
    return [{"timestamp": r.timestamp, "results": r.results} for r in records]
