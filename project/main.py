import jwt
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, ConfigDict, EmailStr

# ===== КОНФИГ =====
DATABASE_URL = "sqlite:///./vex.db"
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===== БД =====
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель User (без пароля)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    avatar_letter = Column(String(1), nullable=True)
    link = Column(String(200), nullable=True)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)

Base.metadata.create_all(bind=engine)

# ===== СХЕМЫ PYDANTIC =====
class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str]
    phone: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageCreate(BaseModel):
    text: str

class MessageOut(BaseModel):
    id: int
    user_id: int
    text: str
    timestamp: datetime

class ChatOut(BaseModel):
    id: int
    name: str
    avatar_letter: Optional[str]
    link: Optional[str]

# ===== ЗАВИСИМОСТИ =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Неверный токен")

# ===== ПРИЛОЖЕНИЕ =====
app = FastAPI(title="VEX Chat API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/chatt.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# ===== РЕГИСТРАЦИЯ (без пароля) =====
@app.post("/register", response_class=JSONResponse)
async def register(
    username: str = Form(...),
    full_name: str = Form(...),
    email: Optional[str] = Form(None),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    # Проверки уникальности
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Имя занято")
    if db.query(User).filter(User.phone == phone).first():
        raise HTTPException(status_code=400, detail="Телефон уже зарегистрирован")
    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email уже используется")

    new_user = User(
        username=username,
        full_name=full_name,
        email=email,
        phone=phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token_data = {
        "sub": str(new_user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(new_user).model_dump()
    }

# ===== ЛОГИН (без пароля, только проверка существования) =====
@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    token_data = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# ===== ОСТАЛЬНЫЕ ЭНДПОИНТЫ (профиль, чаты, сообщения и т.д.) =====
@app.get("/api/profile", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/chats", response_model=List[ChatOut])
async def get_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    participant_chat_ids = db.query(Participant.chat_id).filter(Participant.user_id == current_user.id).subquery()
    chats = db.query(Chat).filter(Chat.id.in_(participant_chat_ids)).all()
    return chats

@app.get("/api/chats/{chat_id}/messages", response_model=List[MessageOut])
async def get_messages(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    participant = db.query(Participant).filter(Participant.user_id == current_user.id, Participant.chat_id == chat_id).first()
    if not participant:
        raise HTTPException(status_code=403, detail="Вы не участник")
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp).all()
    return messages

@app.post("/api/chats/{chat_id}/messages", response_model=MessageOut)
async def send_message(
    chat_id: int,
    msg: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    participant = db.query(Participant).filter(Participant.user_id == current_user.id, Participant.chat_id == chat_id).first()
    if not participant:
        raise HTTPException(status_code=403, detail="Вы не участник")
    new_msg = Message(chat_id=chat_id, user_id=current_user.id, text=msg.text, timestamp=datetime.now(timezone.utc))
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@app.post("/api/chats", response_model=ChatOut)
async def create_chat(
    name: str,
    avatar_letter: Optional[str] = None,
    link: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat = Chat(name=name, avatar_letter=avatar_letter, link=link)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    participant = Participant(user_id=current_user.id, chat_id=chat.id)
    db.add(participant)
    db.commit()
    return chat

@app.post("/api/chats/{chat_id}/add_user")
async def add_user_to_chat(
    chat_id: int,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if db.query(Participant).filter(Participant.user_id == user.id, Participant.chat_id == chat_id).first():
        raise HTTPException(status_code=400, detail="Уже участник")
    new_part = Participant(user_id=user.id, chat_id=chat_id)
    db.add(new_part)
    db.commit()
    return {"detail": f"Пользователь {username} добавлен"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)