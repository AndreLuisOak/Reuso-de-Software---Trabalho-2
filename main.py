from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db import Base, engine, get_db
import models, schemas, auth_utils, email_service
from models import User, RefreshToken
from auth_utils import hash_password, verify_password, create_access_token, create_refresh_token
import uuid
import jwt
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str):
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def save_refresh_token(db: Session, user_id: int, token: str):
    rt = RefreshToken(user_id=user_id, token=token)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt

def revoke_refresh_token(db: Session, token: str):
    rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if rt:
        rt.revoked = True
        db.add(rt)
        db.commit()
    return rt

def verify_refresh_token_record(db: Session, token: str):
    rt = db.query(RefreshToken).filter(RefreshToken.token == token, RefreshToken.revoked == False).first()
    return rt

# Endpoints

@app.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, payload.email, payload.password)
    return user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id), "jti": str(uuid.uuid4())})
    save_refresh_token(db, user.id, refresh)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@app.post("/refresh", response_model=schemas.Token)
def refresh_token(payload: dict, db: Session = Depends(get_db)):
    # esperar {"refresh_token": "..."} no corpo
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing refresh token")
    try:
        decoded = jwt.decode(token, auth_utils.JWT_SECRET, algorithms=[auth_utils.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    record = verify_refresh_token_record(db, token)
    if not record:
        raise HTTPException(status_code=401, detail="Refresh token revoked or unknown")
    user_id = int(decoded.get("sub"))
    access = create_access_token({"sub": str(user_id)})
    # Optionally rotate refresh token:
    new_refresh = create_refresh_token({"sub": str(user_id), "jti": str(uuid.uuid4())})
    record.revoked = True
    db.add(record)
    db.commit()
    save_refresh_token(db, user_id, new_refresh)
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}

@app.post("/logout")
def logout(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing refresh token")
    revoke_refresh_token(db, token)
    return {"ok": True}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth_utils.JWT_SECRET, algorithms=[auth_utils.JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/me", response_model=schemas.UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@app.post("/request-reset")
def request_reset(body: dict, db: Session = Depends(get_db)):
    email = body.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    user = get_user_by_email(db, email)
    if not user:
        return {"ok": True}
    token = create_refresh_token({"sub": str(user.id), "purpose": "password_reset", "jti": str(uuid.uuid4())})
    try:
        email_service.send_email(user.email, "Password reset", f"Use this token to reset: {token}")
    except Exception as e:
        raise HTTPException(status_code=503, detail="Unable to send reset email at this time")
    return {"ok": True}

@app.post("/reset")
def reset_password(body: dict, db: Session = Depends(get_db)):
    token = body.get("token")
    new_password = body.get("new_password")
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="token and new_password required")
    try:
        decoded = jwt.decode(token, auth_utils.JWT_SECRET, algorithms=[auth_utils.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if decoded.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid token purpose")
    user_id = int(decoded.get("sub"))
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()
    return {"ok": True}