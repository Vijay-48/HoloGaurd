from sqlalchemy.orm import Session
from auth import models, security

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password: str):
    hashed = security.get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed)
    db.add(user); db.commit(); db.refresh(user)
    return user

def create_history(db: Session, user_id: int, results: dict):
    record = models.ScanHistory(user_id=user_id, results=str(results))
    db.add(record); db.commit(); db.refresh(record)
    return record

def get_history_for_user(db: Session, user_id: int):
    return db.query(models.ScanHistory).filter(models.ScanHistory.user_id == user_id).all()
