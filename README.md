# 🚀 My-Flask-School

**Современный веб-проект на Flask с крутым темным дизайном и продвинутой системой авторизации**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-red.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

## 🔥 Особенности проекта

### 💡 **Ключевые возможности**
- **🔐 Безопасная авторизация** - CSRF-защита, хэширование паролей, сессии с защитой от подделки
- **🎨 Крутой темный дизайн** - современный UI в стиле GitHub Dark Theme
- **👤 Управление пользователями** - регистрация, вход, профиль, удаление аккаунта
- **🔒 Административные функции** - система ролей (пользователь/админ)
- **📱 Адаптивный интерфейс** - отлично выглядит на всех устройствах

### 🛡️ **Безопасность на высшем уровне**
- ✅ CSRF-защита на всех формах
- ✅ Хэширование паролей с использованием Werkzeug
- ✅ Защита сессий (HTTPOnly, Secure, SameSite)
- ✅ Валидация данных на сервере
- ✅ Защита от SQL-инъекций через ORM

## 🏗️ **Архитектура проекта**

```
My-Flask-School/
    ├── backend
    │   ├── blueprints
    │   │   ├── all_bpp.py
    │   │   ├── errors_handlers.py
    │   │   └── testing_errors_handlers.py
    │   ├── handlers
    │   │   ├── __init__403.py
    │   │   ├── __init__404.py
    │   │   ├── __init__405.py
    │   │   ├── __init__415.py
    │   │   └── __init__500.py
    │   ├── models
    │   │   ├── users
    │   │   │   └── main_user_db.py
    │   │   ├── imp.py
    │   │   └── models_all_rout_imp.py
    │   ├── routers
    │   │   ├── checks
    │   │   │   └── oauth
    │   │   │       ├── login.py
    │   │   │       ├── logout.py
    │   │   │       └── register.py
    │   │   ├── home
    │   │   │   ├── homes.py
    │   │   │   ├── main_home.py
    │   │   │   └── profile.py
    │   │   └── swagger_bp.py
    │   ├── utils
    │   │   ├── testing
    │   │   │   ├── forbidden_error_403.py
    │   │   │   ├── internal_server_error_500.py
    │   │   │   ├── method_not_allowed_error_405.py
    │   │   │   ├── not_found_error_404.py
    │   │   │   └── unsupported_media_type_error_415.py
    │   │   └── swagger_generator.py
    │   ├── app.py
    │   └── config.py
    ├── frontend
    │   ├── static
    │   │   ├── css
    │   │   │   ├── errors
    │   │   │   │   └── css
    │   │   │   │       └── all_css_errors.css
    │   │   │   ├── mod
    │   │   │   │   ├── thems-dark.css
    │   │   │   │   └── thems-light.css
    │   │   │   └── index.css
    │   │   └── js
    │   │       └── index.js
    │   └── templates
    │       ├── errors
    │       │   ├── 403.html
    │       │   ├── 404.html
    │       │   ├── 405.html
    │       │   ├── 415.html
    │       │   ├── 451.html
    │       │   └── 500.html
    │       ├── base.html
    │       ├── home-base.html
    │       ├── home.html
    │       ├── index.html
    │       ├── login.html
    │       ├── profile.html
    │       ├── register.html
    │       └── swagger.html
    ├── .gitignore
    ├── docker-compose.yml
    ├── Dockerfile
    ├── README.md
    └── requirements.txt

```

## 🎯 **Функциональность**

### **📋 Страницы и маршруты**
- `/` - Главная страница
- `/login` - Вход в систему
- `/register` - Регистрация нового пользователя
- `/home` - Личный кабинет (требует авторизации)
- `/profile` - Управление профилем
- `/logout` - Выход из системы

### **👥 Управление пользователями**
- Регистрация с уникальными username и email
- Безопасная аутентификация
- Профиль пользователя с возможностью удаления аккаунта
- Система активности пользователей
- Административные привилегии

## 🚀 **Быстрый старт**

### **📋 Требования**
- Python 3.8+
- Flask 2.0+
- SQLite (встроен в Python)

### **⚙️ Установка и запуск**

1. **Клонируй репозиторий**
```bash
git clone https://github.com/pablaofficeal/My-Flask-School.git
cd My-Flask-School
```

2. **Установи зависимости**
```bash
pip install -r requirements.txt
```

3. **Запусти приложение**
```bash
cd backend
python app.py
```

4. **Открой в браузере**
```
http://localhost:5000
```
### **📄 Документация API**
- **Swagger UI** - интерактивная документация API
- **JSON спецификация** - `/api/swagger.json`

в браузере перейдите по адресу:
```
http://localhost:5000/api/docs
```
Там будет всё, что нужно для работы с API.

## 🎨 **Дизайн и стили**

Проект использует **крутой темный дизайн** в стиле GitHub:
- 🌑 Темная цветовая схема
- 🌈 Акцентные цвета (зеленый, красный, желтый, синий)
- 📱 Адаптивная верстка
- ✨ Современные тени и эффекты
- 🎯 Интуитивный интерфейс

## 🔧 **Конфигурация**

### **⚙️ Основные настройки (config.py)**
```python
SECRET_KEY = 'your_secret_key'           # Смени на свой секретный ключ!
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SESSION_COOKIE_SECURE = False           # В продакшене установи True
WTF_CSRF_ENABLED = True                 # CSRF защита
```

### **🔐 Безопасность в продакшене**
- Установи `SESSION_COOKIE_SECURE = True`
- Смени `SECRET_KEY` на случайный набор символов
- Используй переменные окружения для чувствительных данных
- Добавь HTTPS

## 🛠️ **Технологический стек**

### **Backend**
- **Flask** - веб-фреймворк
- **Flask-SQLAlchemy** - ORM для работы с БД
- **Flask-WTF** - формы и валидация
- **Werkzeug** - безопасность и криптография

### **Frontend**
- **HTML5** - структура
- **CSS3** - стили и анимации
- **Jinja2** - шаблонизатор

### **База данных**
- **SQLite** - легковесная БД для разработки
- **SQLAlchemy ORM** - удобная работа с данными

## 📊 **Модели данных**

### **👤 User (Пользователь)**
- `id` - уникальный идентификатор
- `username` - имя пользователя (уникальное)
- `email` - email (уникальный)
- `password_hash` - хэш пароля
- `created_at` - дата регистрации
- `is_active` - активность аккаунта
- `last_login` - последний вход
- `is_admin` - административные права

## 🔮 **Планы по развитию**

### **🎯 Ближайшие обновления**
- [ ] Email подтверждение при регистрации
- [ ] Восстановление пароля
- [ ] Аватарки пользователей
- [ ] Система уведомлений
- [ ] API для мобильных приложений

### **🚀 Долгосрочные цели**
- [ ] Мультиязычность (i18n)
- [ ] Интеграция с соцсетями
- [ ] Система ролей и прав доступа
- [ ] Админ-панель
- [ ] Статистика и аналитика

## 🤝 **Вклад в проект**

Хочешь помочь? Отлично! Вот как ты можешь внести вклад:

1. 🍴 Форкни репозиторий
2. 🌿 Создай ветку для своей функции (`git checkout -b feature/AmazingFeature`)
3. 💻 Напиши код и закоммить (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Запушь в ветку (`git push origin feature/AmazingFeature`)
5. 📋 Открой Pull Request

## 📝 **Лицензия**

Этот проект распространяется под лицензией MIT. Подробности в файле `LICENSE`.

## 👨‍💻 **Автор**

**PablaOfficeal**

- 🐙 GitHub: [@PablaOfficeal](https://github.com/PablaOfficeal)

---

## ⭐ **Поддержи проект**

Если тебе понравился этот проект, поставь ⭐ на GitHub!

**Made with ❤️ and Python**