# ==========================================
# ПРОЕКТ "ЗА ДЕЛО" v2 - ПЛАТФОРМА ДЛЯ ПОИСКА РАБОТЫ
# ==========================================

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from typing import List, Optional
import enum
import hashlib
import secrets

# ==========================================
# 1. БАЗА ДАННЫХ И МОДЕЛИ
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./zadelo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RoleEnum(str, enum.Enum):
    worker = "worker"
    employer = "employer"
    admin = "admin"

class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    login_id = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default=RoleEnum.worker)
    description = Column(Text, default="") # Новое поле: описание профиля
    token = Column(String, unique=True, index=True, nullable=True)

class DBJob(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    employer_id = Column(Integer, ForeignKey("users.id"))
    
    employer = relationship("DBUser")
    applications = relationship("DBApplication", back_populates="job", cascade="all, delete-orphan")

class DBApplication(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    worker_id = Column(Integer, ForeignKey("users.id"))
    
    job = relationship("DBJob", back_populates="applications")
    worker = relationship("DBUser")

class DBMessage(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)
    
    sender = relationship("DBUser", foreign_keys=[sender_id])
    receiver = relationship("DBUser", foreign_keys=[receiver_id])

Base.metadata.create_all(bind=engine)

# ==========================================
# 2. СХЕМЫ (Pydantic)
# ==========================================
class UserCreate(BaseModel):
    name: str
    login_id: str
    password: str
    role: str

class UserLogin(BaseModel):
    login_id: str
    password: str

class UserProfileUpdate(BaseModel):
    description: str

class JobCreate(BaseModel):
    title: str
    description: str

class MessageCreate(BaseModel):
    receiver_id: int
    text: str

# ==========================================
# 3. FASTAPI API МАРШРУТЫ
# ==========================================
app = FastAPI(title="ЗаДело API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Необходима авторизация")
    user = db.query(DBUser).filter(DBUser.token == authorization).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный токен")
    return user

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/api/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(DBUser).filter(DBUser.login_id == data.login_id).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user = DBUser(name=data.name, login_id=data.login_id, password_hash=hash_password(data.password), role=data.role, token=secrets.token_hex(16))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "role": user.role, "token": user.token, "description": user.description}

@app.post("/api/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.login_id == data.login_id).first()
    if not user or user.password_hash != hash_password(data.password):
        raise HTTPException(status_code=401, detail="Неверные данные")
    user.token = secrets.token_hex(16)
    db.commit()
    return {"id": user.id, "name": user.name, "role": user.role, "token": user.token, "description": user.description}

@app.put("/api/profile")
def update_profile(data: UserProfileUpdate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    user.description = data.description
    db.commit()
    return {"message": "Профиль обновлен", "description": user.description}

@app.get("/api/jobs")
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(DBJob).all()
    return [{"id": j.id, "title": j.title, "description": j.description, "employer_id": j.employer_id, "employer_name": j.employer.name} for j in jobs]

@app.get("/api/my-jobs")
def get_my_jobs(user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "employer":
        raise HTTPException(status_code=403, detail="Только для работодателей")
    jobs = db.query(DBJob).filter(DBJob.employer_id == user.id).all()
    result = []
    for j in jobs:
        apps = [{"worker_id": a.worker.id, "worker_name": a.worker.name, "worker_desc": a.worker.description} for a in j.applications]
        result.append({"id": j.id, "title": j.title, "description": j.description, "applications": apps})
    return result

@app.post("/api/jobs")
def create_job(data: JobCreate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "employer":
        raise HTTPException(status_code=403, detail="Только работодатели могут создавать вакансии")
    job = DBJob(title=data.title, description=data.description, employer_id=user.id)
    db.add(job)
    db.commit()
    return {"message": "Вакансия создана"}

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(DBJob).filter(DBJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    if user.role != "admin" and job.employer_id != user.id:
        raise HTTPException(status_code=403, detail="Вы не можете удалить эту вакансию")
    db.delete(job)
    db.commit()
    return {"message": "Вакансия удалена"}

@app.post("/api/jobs/{job_id}/apply")
def apply_job(job_id: int, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "worker":
        raise HTTPException(status_code=403, detail="Только работники откликаются")
    
    # Проверка, не откликался ли уже
    existing = db.query(DBApplication).filter(DBApplication.job_id == job_id, DBApplication.worker_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже откликнулись")
        
    app = DBApplication(job_id=job_id, worker_id=user.id)
    db.add(app)
    db.commit()
    return {"message": "Отклик отправлен"}

@app.post("/api/messages")
def send_message(data: MessageCreate, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = DBMessage(sender_id=user.id, receiver_id=data.receiver_id, text=data.text)
    db.add(msg)
    db.commit()
    return {"message": "Сообщение отправлено"}

@app.get("/api/messages/{other_user_id}")
def get_messages(other_user_id: int, user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    msgs = db.query(DBMessage).filter(
        ((DBMessage.sender_id == user.id) & (DBMessage.receiver_id == other_user_id)) |
        ((DBMessage.sender_id == other_user_id) & (DBMessage.receiver_id == user.id))
    ).all()
    return [{"sender_id": m.sender_id, "text": m.text} for m in msgs]


# ==========================================
# 4. ВСТРОЕННЫЙ FRONTEND (HTML + JS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ЗаДело - Быстрый поиск работы</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .hidden { display: none !important; }
        body { background-color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
</head>
<body class="text-slate-800">

    <nav class="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
            <h1 class="text-2xl font-bold text-blue-600 cursor-pointer" onclick="showPage('home')">ЗаДело</h1>
            <div id="nav-unauth">
                <button onclick="showPage('login')" class="text-slate-600 hover:text-blue-600 mr-4 font-medium">Вход</button>
                <button onclick="showPage('register')" class="bg-blue-600 text-white px-5 py-2 rounded-full font-medium hover:bg-blue-700">Регистрация</button>
            </div>
            <div id="nav-auth" class="hidden flex items-center space-x-4">
                <button onclick="showPage('profile')" class="text-slate-600 font-medium hover:text-blue-600">Мой профиль</button>
                <button onclick="logout()" class="text-red-500 font-medium hover:text-red-700">Выйти</button>
            </div>
        </div>
    </nav>

    <main class="max-w-5xl mx-auto px-4 py-8">
        
        <!-- ГЛАВНАЯ СТРАНИЦА -->
        <section id="page-home">
            <div id="hero-banner" class="text-center py-10 mb-8 bg-white rounded-2xl shadow-sm border border-slate-100">
                <h2 class="text-4xl font-extrabold text-slate-800 mb-4">Дело есть для каждого</h2>
                <p class="text-lg text-slate-500 max-w-2xl mx-auto">Платформа быстрой подработки.</p>
            </div>

            <!-- Панель работодателя -->
            <div id="employer-panel" class="hidden mb-8 bg-blue-50 p-6 rounded-2xl border border-blue-100">
                <h3 class="text-xl font-bold mb-4 text-blue-800">Разместить задачу</h3>
                <input id="job-title" type="text" placeholder="Заголовок (например: Разгрузить фуру)" class="w-full mb-3 p-3 rounded-lg border border-slate-300">
                <textarea id="job-desc" placeholder="Описание задачи..." class="w-full mb-3 p-3 rounded-lg border border-slate-300 h-24"></textarea>
                <button onclick="createJob()" class="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700">Разместить</button>
            </div>

            <h3 class="text-2xl font-bold mb-4">Доска объявлений</h3>
            <div id="jobs-container" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
        </section>

        <!-- ПРОФИЛЬ И УПРАВЛЕНИЕ -->
        <section id="page-profile" class="hidden">
            <h2 class="text-3xl font-bold mb-6">Личный кабинет</h2>
            
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-8">
                <h3 class="text-xl font-bold mb-4" id="profile-name"></h3>
                <p class="text-sm text-slate-500 mb-2 uppercase tracking-wide" id="profile-role"></p>
                <label class="block font-medium mb-2">О себе / О компании:</label>
                <textarea id="profile-desc" class="w-full mb-3 p-3 rounded-lg border border-slate-300 h-32"></textarea>
                <button onclick="updateProfile()" class="bg-green-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700">Сохранить описание</button>
            </div>

            <!-- Секция для работодателей (Мои вакансии и отклики) -->
            <div id="my-jobs-section" class="hidden">
                <h3 class="text-2xl font-bold mb-4">Мои объявления и отклики</h3>
                <div id="my-jobs-container" class="space-y-4"></div>
            </div>
        </section>

        <!-- ЧАТ И ПРОСМОТР КАНДИДАТА -->
        <section id="page-chat" class="hidden max-w-2xl mx-auto">
            <button onclick="showPage('profile')" class="text-blue-600 mb-4 font-medium">&larr; Назад</button>
            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-4">
                <h3 class="text-xl font-bold" id="chat-partner-name"></h3>
                <p class="text-slate-600 mt-2 bg-slate-50 p-3 rounded" id="chat-partner-desc"></p>
            </div>
            
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
                <div id="chat-messages" class="h-64 overflow-y-auto mb-4 space-y-2 p-2 border-b border-slate-100"></div>
                <div class="flex gap-2">
                    <input id="chat-input" type="text" placeholder="Написать сообщение..." class="flex-1 p-3 rounded-lg border border-slate-300">
                    <button onclick="sendMessage()" class="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium">Отправить</button>
                </div>
            </div>
        </section>

        <!-- ВХОД / РЕГИСТРАЦИЯ -->
        <section id="page-login" class="hidden max-w-md mx-auto bg-white p-8 rounded-2xl shadow-sm border border-slate-100 mt-10">
            <h2 class="text-2xl font-bold mb-6 text-center">Вход</h2>
            <input id="login-id" type="text" placeholder="Телефон или Email" class="w-full mb-4 p-3 rounded-lg border border-slate-300">
            <input id="login-pwd" type="password" placeholder="Пароль" class="w-full mb-6 p-3 rounded-lg border border-slate-300">
            <button onclick="login()" class="w-full bg-blue-600 text-white py-3 rounded-lg font-medium">Войти</button>
        </section>

        <section id="page-register" class="hidden max-w-md mx-auto bg-white p-8 rounded-2xl shadow-sm border border-slate-100 mt-10">
            <h2 class="text-2xl font-bold mb-6 text-center">Регистрация</h2>
            <input id="reg-name" type="text" placeholder="Ваше Имя (ФИО)" class="w-full mb-4 p-3 rounded-lg border border-slate-300">
            <input id="reg-id" type="text" placeholder="Телефон или Email" class="w-full mb-4 p-3 rounded-lg border border-slate-300">
            <input id="reg-pwd" type="password" placeholder="Пароль" class="w-full mb-4 p-3 rounded-lg border border-slate-300">
            <select id="reg-role" class="w-full mb-6 p-3 rounded-lg border border-slate-300 bg-white">
                <option value="worker">Я работник (ищу задачи)</option>
                <option value="employer">Я заказчик (даю задачи)</option>
                <option value="admin">Администратор (для модерации)</option>
            </select>
            <button onclick="register()" class="w-full bg-green-600 text-white py-3 rounded-lg font-bold">Создать аккаунт</button>
        </section>

    </main>

    <script>
        let currentUser = JSON.parse(localStorage.getItem('zadelo_user')) || null;
        let currentChatPartnerId = null;
        const API_URL = '/api';

        window.onload = () => {
            updateUI();
            loadJobs();
        };

        function showPage(pageId) {
            document.querySelectorAll('main > section').forEach(s => s.classList.add('hidden'));
            document.getElementById('page-' + pageId).classList.remove('hidden');
            if (pageId === 'home') loadJobs();
            if (pageId === 'profile') loadProfileData();
        }

        function updateUI() {
            if (currentUser) {
                document.getElementById('nav-unauth').classList.add('hidden');
                document.getElementById('nav-auth').classList.remove('hidden');
                
                // Админ не видит форму создания вакансии
                if (currentUser.role === 'employer') {
                    document.getElementById('employer-panel').classList.remove('hidden');
                    document.getElementById('my-jobs-section').classList.remove('hidden');
                } else {
                    document.getElementById('employer-panel').classList.add('hidden');
                    document.getElementById('my-jobs-section').classList.add('hidden');
                }
            } else {
                document.getElementById('nav-unauth').classList.remove('hidden');
                document.getElementById('nav-auth').classList.add('hidden');
                document.getElementById('employer-panel').classList.add('hidden');
            }
        }

        async function register() {
            const data = {
                name: document.getElementById('reg-name').value,
                login_id: document.getElementById('reg-id').value,
                password: document.getElementById('reg-pwd').value,
                role: document.getElementById('reg-role').value
            };
            try {
                const res = await fetch(`${API_URL}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                if (!res.ok) throw new Error(await res.text());
                currentUser = await res.json();
                localStorage.setItem('zadelo_user', JSON.stringify(currentUser));
                updateUI(); showPage('home');
            } catch (e) { alert("Ошибка: " + e.message); }
        }

        async function login() {
            const data = { login_id: document.getElementById('login-id').value, password: document.getElementById('login-pwd').value };
            try {
                const res = await fetch(`${API_URL}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                if (!res.ok) throw new Error("Неверные данные");
                currentUser = await res.json();
                localStorage.setItem('zadelo_user', JSON.stringify(currentUser));
                updateUI(); showPage('home');
            } catch (e) { alert(e.message); }
        }

        function logout() {
            currentUser = null; localStorage.removeItem('zadelo_user');
            updateUI(); showPage('home');
        }

        async function updateProfile() {
            const desc = document.getElementById('profile-desc').value;
            try {
                const res = await fetch(`${API_URL}/profile`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'Authorization': currentUser.token },
                    body: JSON.stringify({ description: desc })
                });
                if (res.ok) {
                    currentUser.description = desc;
                    localStorage.setItem('zadelo_user', JSON.stringify(currentUser));
                    alert("Профиль сохранен!");
                }
            } catch (e) { alert("Ошибка сохранения"); }
        }

        function loadProfileData() {
            if(!currentUser) return;
            document.getElementById('profile-name').innerText = currentUser.name;
            document.getElementById('profile-role').innerText = "Роль: " + currentUser.role;
            document.getElementById('profile-desc').value = currentUser.description || "";
            if (currentUser.role === 'employer') loadMyJobs();
        }

        async function loadJobs() {
            try {
                const res = await fetch(`${API_URL}/jobs`);
                const jobs = await res.json();
                const container = document.getElementById('jobs-container');
                container.innerHTML = '';
                
                jobs.forEach(job => {
                    let actionBtn = '';
                    if (currentUser) {
                        if (currentUser.role === 'worker') {
                            actionBtn = `<button onclick="applyJob(${job.id})" class="mt-4 w-full bg-blue-100 text-blue-700 font-medium py-2 rounded hover:bg-blue-200">Откликнуться</button>`;
                        } else if (currentUser.role === 'admin' || (currentUser.role === 'employer' && currentUser.id === job.employer_id)) {
                            actionBtn = `<button onclick="deleteJob(${job.id})" class="mt-4 w-full bg-red-100 text-red-700 font-medium py-2 rounded hover:bg-red-200">Удалить объявление</button>`;
                        }
                    }
                    container.innerHTML += `
                        <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200">
                            <h4 class="text-lg font-bold">${job.title}</h4>
                            <p class="text-slate-600 text-sm mb-4">${job.description}</p>
                            <div class="text-xs font-semibold text-slate-400">Заказчик: ${job.employer_name}</div>
                            ${actionBtn}
                        </div>`;
                });
            } catch (e) { console.error(e); }
        }

        async function loadMyJobs() {
            try {
                const res = await fetch(`${API_URL}/my-jobs`, { headers: { 'Authorization': currentUser.token } });
                const jobs = await res.json();
                const container = document.getElementById('my-jobs-container');
                container.innerHTML = '';
                
                jobs.forEach(job => {
                    let applicantsHtml = job.applications.map(app => `
                        <div class="flex justify-between items-center bg-slate-50 p-3 rounded mt-2 border border-slate-200">
                            <div>
                                <span class="font-bold">${app.worker_name}</span> хочет взяться за дело.
                            </div>
                            <button onclick="openChat(${app.worker_id}, '${app.worker_name}', '${app.worker_desc || "Нет описания"}')" class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">Посмотреть & Написать</button>
                        </div>
                    `).join('');

                    if (job.applications.length === 0) applicantsHtml = '<p class="text-sm text-slate-400 mt-2">Пока нет откликов</p>';

                    container.innerHTML += `
                        <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200 border-l-4 border-l-blue-500">
                            <h4 class="text-lg font-bold">${job.title}</h4>
                            <div class="mt-4 border-t border-slate-100 pt-3">
                                <h5 class="font-semibold text-slate-700">Отклики:</h5>
                                ${applicantsHtml}
                            </div>
                        </div>`;
                });
            } catch (e) { console.error(e); }
        }

        async function createJob() {
            const data = { title: document.getElementById('job-title').value, description: document.getElementById('job-desc').value };
            await fetch(`${API_URL}/jobs`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': currentUser.token }, body: JSON.stringify(data) });
            document.getElementById('job-title').value = '';
            document.getElementById('job-desc').value = '';
            loadJobs();
        }

        async function applyJob(jobId) {
            try {
                const res = await fetch(`${API_URL}/jobs/${jobId}/apply`, { method: 'POST', headers: { 'Authorization': currentUser.token } });
                if (!res.ok) throw new Error(await res.text());
                alert("Успешно! Вы откликнулись.");
            } catch (e) { alert("Ошибка: Вы уже откликнулись на эту вакансию"); }
        }

        async function deleteJob(jobId) {
            if(!confirm("Точно удалить?")) return;
            await fetch(`${API_URL}/jobs/${jobId}`, { method: 'DELETE', headers: { 'Authorization': currentUser.token } });
            loadJobs();
            if(currentUser.role === 'employer') loadMyJobs();
        }

        // Логика чата
        function openChat(workerId, workerName, workerDesc) {
            currentChatPartnerId = workerId;
            document.getElementById('chat-partner-name').innerText = "Кандидат: " + workerName;
            document.getElementById('chat-partner-desc').innerText = "О себе: " + workerDesc;
            showPage('chat');
            loadMessages();
        }

        async function loadMessages() {
            if (!currentChatPartnerId) return;
            const res = await fetch(`${API_URL}/messages/${currentChatPartnerId}`, { headers: { 'Authorization': currentUser.token } });
            const msgs = await res.json();
            const container = document.getElementById('chat-messages');
            container.innerHTML = msgs.map(m => {
                const isMine = m.sender_id === currentUser.id;
                return `<div class="p-2 my-1 rounded-lg w-3/4 ${isMine ? 'bg-blue-100 ml-auto' : 'bg-slate-100'}">${m.text}</div>`;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('chat-input');
            if(!input.value.trim()) return;
            await fetch(`${API_URL}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': currentUser.token },
                body: JSON.stringify({ receiver_id: currentChatPartnerId, text: input.value })
            });
            input.value = '';
            loadMessages();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return HTML_TEMPLATE

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)