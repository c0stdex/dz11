from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash

def get_user(db: Session, user_id: int):
    """
    Отримує користувача за його ідентифікатором.

    Args:
        db (Session): Сесія бази даних.
        user_id (int): Ідентифікатор користувача.

    Returns:
        models.User: Користувач.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """
    Отримує користувача за його електронною адресою.

    Args:
        db (Session): Сесія бази даних.
        email (str): Електронна адреса користувача.

    Returns:
        models.User: Користувач.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Створює нового користувача у базі даних.

    Args:
        db (Session): Сесія бази даних.
        user (schemas.UserCreate): Схема даних для створення користувача.

    Returns:
        models.User: Створений користувач.
    """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    """
    Створює новий контакт для користувача.

    Args:
        db (Session): Сесія бази даних.
        contact (schemas.ContactCreate): Схема даних для створення контакту.
        user_id (int): Ідентифікатор користувача.

    Returns:
        models.Contact: Створений контакт.
    """
    db_contact = models.Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Отримує список контактів для користувача.

    Args:
        db (Session): Сесія бази даних.
        user_id (int): Ідентифікатор користувача.
        skip (int): Кількість пропущених записів.
        limit (int): Максимальна кількість записів.

    Returns:
        List[models.Contact]: Список контактів.
    """
    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Отримує контакт за його ідентифікатором та ідентифікатором користувача.

    Args:
        db (Session): Сесія бази даних.
        contact_id (int): Ідентифікатор контакту.
        user_id (int): Ідентифікатор користувача.

    Returns:
        models.Contact: Контакт.
    """
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user_id: int):
    """
    Оновлює контакт за його ідентифікатором та ідентифікатором користувача.

    Args:
        db (Session): Сесія бази даних.
        contact_id (int): Ідентифікатор контакту.
        contact (schemas.ContactUpdate): Схема даних для оновлення контакту.
        user_id (int): Ідентифікатор користувача.

    Returns:
        models.Contact: Оновлений контакт.
    """
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        for key, value in contact.dict(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Видаляє контакт за його ідентифікатором та ідентифікатором користувача.

    Args:
        db (Session): Сесія бази даних.
        contact_id (int): Ідентифікатор контакту.
        user_id (int): Ідентифікатор користувача.

    Returns:
        models.Contact: Видалений контакт.
    """
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact
