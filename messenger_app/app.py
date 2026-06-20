from flask import Flask, render_template, request, jsonify
import time
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Настройки подключения к MySQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'messenger_db',
    'user': 'root',      # замените на своего пользователя
    'password': '1234'   # замените на свой пароль
}

# Функция для получения соединения
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None

# Инициализация базы данных (создание таблиц, если не существуют)
def init_db():
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            fullname VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50) NOT NULL
        )
    ''')
    # Таблица сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id INT NOT NULL,
            text TEXT NOT NULL,
            time VARCHAR(5) NOT NULL,
            type ENUM('sent', 'received') NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    print("База данных инициализирована")

# Вызов инициализации при старте
init_db()

# Функция для добавления дефолтных сообщений (если чаты пусты)
def seed_default_messages():
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    # Проверим, есть ли сообщения для чата 1
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = 1")
    count = cursor.fetchone()[0]
    if count == 0:
        default_msgs = [
            (1, "Го дружить", "17:15", "sent"),
            (1, "Го Warthander скачаем", "18:21", "sent"),
            (1, "Сегодня в танчики", "15:47", "received"),
            (1, "Сегодня в танки", "15:39", "received"),
        ]
        cursor.executemany(
            "INSERT INTO messages (chat_id, text, time, type) VALUES (%s, %s, %s, %s)",
            default_msgs
        )
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = 2")
    count = cursor.fetchone()[0]
    if count == 0:
        default_msgs = [
            (2, "Привет!", "13:30", "received"),
            (2, "То сегодня на ре...", "13:35", "sent"),
        ]
        cursor.executemany(
            "INSERT INTO messages (chat_id, text, time, type) VALUES (%s, %s, %s, %s)",
            default_msgs
        )
    conn.commit()
    cursor.close()
    conn.close()

seed_default_messages()

# Список чатов (можно вынести в отдельную таблицу, но оставим статику)
CHATS = [
    {"id": 1, "name": "Танки 2024", "avatar": "Т"},
    {"id": 2, "name": "Вася", "avatar": "В"},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    fullname = data.get('fullname', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()

    if not username or not fullname or not phone:
        return jsonify({"status": "error", "message": "Заполните все обязательные поля"})
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Ошибка сервера"})
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, fullname, email, phone) VALUES (%s, %s, %s, %s)",
            (username, fullname, email, phone)
        )
        conn.commit()
        print(f"Registered: {username}")
        return jsonify({"status": "success", "message": "Регистрация успешна"})
    except mysql.connector.IntegrityError:
        return jsonify({"status": "error", "message": "Имя пользователя занято"})
    finally:
        cursor.close()
        conn.close()

@app.route('/chats')
def get_chats():
    conn = get_db_connection()
    if conn is None:
        return jsonify([])
    cursor = conn.cursor()
    chat_list = []
    for chat in CHATS:
        chat_id = chat['id']
        cursor.execute(
            "SELECT text, time FROM messages WHERE chat_id = %s ORDER BY id DESC LIMIT 1",
            (chat_id,)
        )
        last = cursor.fetchone()
        last_text = last[0] if last else "Нет сообщений"
        last_time = last[1] if last else ""
        unread = 2  # можно потом реализовать подсчёт непрочитанных
        chat_list.append({
            "id": chat_id,
            "name": chat['name'],
            "last_message": last_text[:20] + ("..." if len(last_text) > 20 else ""),
            "time": last_time,
            "unread": unread,
            "avatar": chat['avatar']
        })
    cursor.close()
    conn.close()
    return jsonify(chat_list)

@app.route('/messages/<int:chat_id>')
def get_messages(chat_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify([])
    cursor = conn.cursor()
    cursor.execute(
        "SELECT text, time, type FROM messages WHERE chat_id = %s ORDER BY id",
        (chat_id,)
    )
    rows = cursor.fetchall()
    messages = [{"text": r[0], "time": r[1], "type": r[2]} for r in rows]
    cursor.close()
    conn.close()
    return jsonify(messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    chat_id = data.get('chat_id')
    text = data.get('text', '').strip()
    
    if not chat_id or not text:
        return jsonify({"status": "error", "message": "Неверные данные"})
    
    now = time.strftime("%H:%M")
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Ошибка сервера"})
    cursor = conn.cursor()
    # Вставляем сообщение пользователя
    cursor.execute(
        "INSERT INTO messages (chat_id, text, time, type) VALUES (%s, %s, %s, %s)",
        (chat_id, text, now, "sent")
    )
    conn.commit()
    # Забираем все сообщения для этого чата
    cursor.execute(
        "SELECT text, time, type FROM messages WHERE chat_id = %s ORDER BY id",
        (chat_id,)
    )
    rows = cursor.fetchall()
    messages = [{"text": r[0], "time": r[1], "type": r[2]} for r in rows]
    cursor.close()
    conn.close()
    return jsonify(messages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)