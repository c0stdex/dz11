# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_contact(db: Session, user_id: int, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit).all()

def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    db_contact = models.Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def update_contact(db: Session, user_id: int, contact_id: int, contact: schemas.ContactCreate):
    db_contact = get_contact(db, user_id, contact_id)
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, user_id: int, contact_id: int):
    db_contact = get_contact(db, user_id, contact_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def search_contacts(db: Session, user_id: int, query: str):
    return db.query(models.Contact).filter(
        models.Contact.owner_id == user_id,
        (models.Contact.first_name.ilike(f"%{query}%")) |
        (models.Contact.last_name.ilike(f"%{query}%")) |
        (models.Contact.email.ilike(f"%{query}%"))
    ).all()

def get_upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    upcoming_birthdays = db.query(models.Contact).filter(
        models.Contact.owner_id == user_id,
        models.Contact.birthday.between(today, today + timedelta(days=7))
    ).all()
    return upcoming_birthdays
