import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_2006' # Ключ для шифрования сессий браузера

def get_db_connection():
    # os.getenv("DB_PASSWORD") вытащит пароль из скрытых настроек операционной системы ноутбука
    db_password = os.getenv("DB_PASSWORD")
    
    if not db_password:
        raise ValueError("Критическая ошибка: Переменная окружения DB_PASSWORD не задана на сервере!")

    conn = psycopg2.connect(
        host="127.0.0.1",
        database="forum_db",
        user="postgres",
        password=db_password
    )
    return conn

# 1. ГЛАВНАЯ СТРАНИЦА
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT (CURRENT_TIMESTAMP - INTERVAL '7305 days')::timestamp as forum_time;")
        db_time = cursor.fetchone()
        formatted_time = db_time['forum_time'].strftime('%d.%m.%Y %H:%M:%S')
        
        cursor.execute("SELECT id, title, created_at FROM topics ORDER BY id ASC;")
        forum_sections = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('index.html', forum_time=formatted_time, sections=forum_sections)
    except Exception as e:
        return f"<h1>Ошибка базы данных!</h1><p>{str(e)}</p>"

# 2. СТРАНИЦА ПРОСМОТРА ТЕМЫ
@app.route('/topic/<int:topic_id>')
def view_topic(topic_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT id, title FROM topics WHERE id = %s;", (topic_id,))
        topic = cursor.fetchone()
        
        if not topic:
            cursor.close()
            conn.close()
            return "<h1>Тема не найдена!</h1>", 404
            
        query = """
            SELECT posts.id, posts.content, posts.created_at, users.username, users.user_title
            FROM posts
            JOIN users ON posts.author_id = users.id
            WHERE posts.topic_id = %s
            ORDER BY posts.id ASC;
        """
        cursor.execute(query, (topic_id,))
        posts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('topic.html', topic=topic, posts=posts)
    except Exception as e:
        return f"<h1>Ошибка базы данных!</h1><p>{str(e)}</p>"

# 3. СТРАНИЦА С ФОРМАМИ ВХОДА/РЕГИСТРАЦИИ
@app.route('/auth')
def auth_page():
    return render_template('auth.html')

# 4. ЛОГИКА РЕГИСТРАЦИИ
@app.route('/register', methods=['POST'])
def do_register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Хэшируем пароль по ГОСТу веб-безопасности
    hashed_password = generate_password_hash(password)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверяем, нет ли уже такого юзера
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s;", (username, email))
        if cursor.fetchone():
            flash('Ошибка: Пользователь с таким именем или Email уже существует!')
            cursor.close()
            conn.close()
            return redirect(url_for('auth_page'))
            
        # Записываем нового юзера. Дата автоматом упадет в 2006 год благодаря DEFAULT в базе!
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s);",
            (username, hashed_password, email)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('auth_page'))
        
    except Exception as e:
        flash(f'Ошибка БД: {str(e)}')
        return redirect(url_for('auth_page'))

# 5. ЛОГИКА ВХОДА (ЛОГИН)
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT id, username, password_hash, user_title FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Проверяем хэш пароля
        if user and check_password_hash(user['password_hash'], password):
            # Записываем данные юзера в сессию браузера (он залогинен!)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_title'] = user['user_title']
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль!')
            return redirect(url_for('auth_page'))
            
    except Exception as e:
        flash(f'Ошибка БД: {str(e)}')
        return redirect(url_for('auth_page'))

# 6. ВЫХОД ИЗ АККАУНТА
@app.route('/logout')
def do_logout():
    session.clear() # Стираем сессию
    return redirect(url_for('index'))

# 7. ЛОГИКА ОТПРАВКИ ОТВЕТА В ТЕМУ
@app.route('/topic/<int:topic_id>/reply', methods=['POST'])
def do_reply(topic_id):
    # Проверяем, залогинен ли юзер, чтобы боты не спамили
    if not session.get('user_id'):
        return "<h1>Ошибка: Вы должны быть авторизованы!</h1>", 403
        
    content = request.form['content']
    author_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Записываем пост. Время сдвинется на 20 лет назад АВТОМАТИЧЕСКИ на уровне базы данных!
        cursor.execute(
            "INSERT INTO posts (topic_id, author_id, content) VALUES (%s, %s, %s);",
            (topic_id, author_id, content)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Возвращаем пользователя обратно в эту же тему, чтобы он увидел свой пост
        return redirect(url_for('view_topic', topic_id=topic_id))
        
    except Exception as e:
        return f"<h1>Ошибка отправки сообщения в БД!</h1><p>{str(e)}</p>"
    
# 8. ЛОГИКА СОЗДАНИЯ НОВОЙ ТЕМЫ С ГЛАВНОЙ СТРАНИЦЫ
@app.route('/create-topic', methods=['POST'])
def create_topic():
    if not session.get('user_id'):
        return "<h1>Ошибка: Вы должны быть авторизованы!</h1>", 403
        
    title = request.form['title']
    author_id = session['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Вставляем тему в БД. Капсула времени (-20 лет) сработает автоматически!
        cursor.execute(
            "INSERT INTO topics (title, author_id) VALUES (%s, %s);",
            (title, author_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Возвращаем юзера на главную страницу, где он увидит свою новую тему в таблице
        return redirect(url_for('index'))
        
    except Exception as e:
        return f"<h1>Ошибка создания темы в БД!</h1><p>{str(e)}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
