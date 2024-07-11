from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import aioredis
from . import crud, models, schemas, auth, utils, cloudinary_utils
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    auth.redis = await aioredis.create_redis_pool("redis://localhost")
    await FastAPILimiter.init(auth.redis)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/verify-email/")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        user = crud.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_verified = True
        db.commit()
        return {"msg": "Email verified successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db_user = crud.create_user(db=db, user=user)
    verification_token = auth.create_verification_token(data={"sub": user.email})
    utils.send_verification_email(user.email, verification_token)
    return db_user

@app.post("/contacts/", response_model=schemas.Contact, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@app.post("/users/avatar/")
def update_avatar(file: UploadFile = File(...), current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    file_location = f"tmp/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    avatar_url = cloudinary_utils.upload_avatar(file_location)
    current_user.avatar_url = avatar_url
    db.commit()
    return {"avatar_url": avatar_url}

@app.post("/reset-password/")
def reset_password_request(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = auth.create_verification_token(data={"sub": user.email})
    utils.send_reset_password_email(email, reset_token)

@app.post("/reset-password/confirm/")
def reset_password_confirm(token: str, new_password: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        user = crud.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.hashed_password = auth.get_password_hash(new_password)
        db.commit()
        return {"msg": "Password reset successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
