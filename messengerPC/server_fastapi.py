# server_fastapi.py
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
import uvicorn
import json
import os
from datetime import datetime

# ===== МОДЕЛИ ДАННЫХ =====

class Message(BaseModel):
    text: str
    time: str
    sender: str  # 'sent' или 'received'

class Chat(BaseModel):
    id: str
    name: str
    avatarLetter: str
    subtitle: str
    badgeTime: str
    badgeCount: str
    members: List[str]
    link: str
    messages: List[Message]

class UserRegister(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: str
    
    @validator('phone')
    def validate_phone(cls, v):
        # Простая валидация телефона
        if not v or len(v) < 5:
            raise ValueError('Некорректный номер телефона')
        return v

class UserProfile(BaseModel):
    username: str
    full_name: str
    email: Optional[str] = None
    phone: str
    avatar_url: Optional[str] = None

# ===== СОЗДАНИЕ ПРИЛОЖЕНИЯ =====

app = FastAPI(
    title="VEX API",
    description="API для мессенджера VEX",
    version="1.0.0"
)

# ===== ДАННЫЕ (В БОЕВОМ ПРИЛОЖЕНИИ ИСПОЛЬЗУЙТЕ БД) =====

# Данные чатов
chats_data = [
    {
        "id": "tanks",
        "name": "Танки 2024",
        "avatarLetter": "Т",
        "subtitle": "Сегодня в танки",
        "badgeTime": "сб",
        "badgeCount": "34",
        "members": ["Артем Аксенов", "Артём Артемов"],
        "link": "t.me/tanks2024",
        "messages": [
            {"text": "Го дружить", "time": "17:15", "sender": "received"},
            {"text": "Го", "time": "17:15", "sender": "sent"},
            {"text": "Го Warthander скачаем", "time": "18:21", "sender": "received"},
            {"text": "Го", "time": "18:21", "sender": "sent"},
            {"text": "Сегодня в танчики", "time": "11:47", "sender": "received"},
            {"text": "Го", "time": "11:47", "sender": "sent"},
            {"text": "Сегодня в танки", "time": "15:39", "sender": "sent"},
        ]
    },
    {
        "id": "vasya",
        "name": "Вася",
        "avatarLetter": "В",
        "subtitle": "Го сегодня на ре...",
        "badgeTime": "13:35",
        "badgeCount": "2",
        "members": ["Вася", "Петя"],
        "link": "t.me/vasya",
        "messages": [
            {"text": "Привет", "time": "12:00", "sender": "received"},
            {"text": "Здарова", "time": "12:01", "sender": "sent"},
        ]
    }
]

# Данные пользователя (временные)
current_user = {
    "username": "nikita_k",
    "full_name": "Никита Корнейков",
    "email": "nikita@example.com",
    "phone": "+7 960 553 76 58",
    "avatar_url": "https://i.yapx.ru/d3KH0.png"
}

# ===== API ЭНДПОИНТЫ =====

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Главная страница приложения"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html не найден")

@app.get("/f.css", response_class=HTMLResponse)
async def get_css():
    """CSS файл"""
    try:
        with open("f.css", "r", encoding="utf-8") as f:
            css_content = f.read()
        return HTMLResponse(content=css_content, media_type="text/css")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="f.css не найден")

@app.get("/script.js", response_class=HTMLResponse)
async def get_js():
    """JavaScript файл"""
    try:
        with open("script.js", "r", encoding="utf-8") as f:
            js_content = f.read()
        return HTMLResponse(content=js_content, media_type="application/javascript")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="script.js не найден")

# ===== API ДЛЯ ЧАТОВ =====

@app.get("/api/chats", response_model=List[Chat])
async def get_chats():
    """Получение списка всех чатов"""
    return chats_data

@app.get("/api/chats/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str):
    """Получение чата по ID"""
    for chat in chats_data:
        if chat["id"] == chat_id:
            return chat
    raise HTTPException(status_code=404, detail="Чат не найден")

@app.post("/api/chats/{chat_id}/messages")
async def send_message(chat_id: str, message: Message):
    """Отправка сообщения в чат"""
    for chat in chats_data:
        if chat["id"] == chat_id:
            # Добавляем сообщение
            chat["messages"].append(message.dict())
            return {"status": "success", "message": "Сообщение отправлено"}
    raise HTTPException(status_code=404, detail="Чат не найден")

@app.get("/api/chats/{chat_id}/messages")
async def get_messages(chat_id: str):
    """Получение всех сообщений чата"""
    for chat in chats_data:
        if chat["id"] == chat_id:
            return chat["messages"]
    raise HTTPException(status_code=404, detail="Чат не найден")

# ===== API ДЛЯ РЕГИСТРАЦИИ =====

@app.post("/api/register")
async def register_user(user: UserRegister):
    """Регистрация нового пользователя"""
    # В реальном приложении здесь была бы проверка на существование пользователя
    # и сохранение в БД
    
    # Имитация успешной регистрации
    return {
        "status": "success",
        "message": "Регистрация успешна",
        "user": user.dict()
    }

@app.get("/api/profile")
async def get_profile():
    """Получение профиля текущего пользователя"""
    return current_user

@app.put("/api/profile")
async def update_profile(profile: UserProfile):
    """Обновление профиля пользователя"""
    global current_user
    # В реальном приложении здесь было бы обновление в БД
    current_user.update(profile.dict())
    return {
        "status": "success",
        "message": "Профиль обновлен",
        "user": current_user
    }

# ===== API ДЛЯ СООБЩЕСТВ =====

@app.get("/api/communities")
async def get_communities():
    """Получение списка сообществ"""
    # В реальном приложении данные из БД
    communities = [
        {
            "id": 1,
            "name": "Многопрофильный клуб",
            "image": "https://1s4oyld5dc.ucarecd.net/8fd5143c-5a69-4fc4-8297-550dc43f64e6/"
        },
        {
            "id": 2,
            "name": "Русское географическое",
            "image": "https://1s4oyld5dc.ucarecd.net/3f30d429-5ab9-4157-9d9e-753b26a7d1e9/"
        },
        {
            "id": 3,
            "name": "Кафедра ИТ",
            "image": "https://1s4oyld5dc.ucarecd.net/bb50c0a6-df4c-40ab-904f-1f2081191667/"
        },
        {
            "id": 4,
            "name": "Кафедра ОПиПК Б...",
            "image": "https://1s4oyld5dc.ucarecd.net/da549fed-c181-4473-ad10-c359514eea9c/"
        }
    ]
    return communities

@app.post("/api/communities/{community_id}/join")
async def join_community(community_id: int):
    """Вступление в сообщество"""
    # В реальном приложении добавление пользователя в сообщество в БД
    return {
        "status": "success",
        "message": f"Вы вступили в сообщество #{community_id}"
    }

# ===== API ДЛЯ КОНТАКТОВ =====

@app.get("/api/contacts")
async def get_contacts():
    """Получение истории контактов"""
    # В реальном приложении данные из БД
    contacts = [
        {"name": "Артем Аксенов", "date": "Завершённый - 27 мая"},
        {"name": "Артем Аксенов", "date": "Завершённый - 18 мая"},
        {"name": "Артем Аксенов", "date": "Завершённый - 22 апреля"},
    ]
    return contacts

# ===== ЗАПУСК СЕРВЕРА =====

if __name__ == "__main__":
    print("🚀 Запуск FastAPI сервера...")
    print("📱 Откройте в браузере: http://localhost:8000")
    print("📚 Документация API: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)