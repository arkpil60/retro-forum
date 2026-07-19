from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from datetime import datetime
from app.repositories.forum_repo import ForumRepository
from app.repositories.topic_repo import TopicRepository 
from app.repositories.post_repo import PostRepository


forum_bp = Blueprint('forum', __name__)

@forum_bp.route('/')
def index():
    # 1. Запрашиваем из базы данных список всех категорий
    categories_list = ForumRepository.get_all_categories()
    
    # 2. Запрашиваем общую статистику форума (кол-во юзеров, тем, постов)
    stats = ForumRepository.get_forum_stats()
    
    # 3. Запрашиваем список имен пользователей, которые сейчас онлайн
    online_users_list = ForumRepository.get_online_users()
    
    # 4. Берем точное текущее время на сервере для ретро-часов
    now = datetime.now()
    
    # 5. Рендерим главную страницу, передавая туда ВСЕ собранные данные
    return render_template(
        'forum/index.html', 
        current_time=now, 
        categories=categories_list,
        stats=stats,
        online_users=online_users_list
    )

@forum_bp.route('/category/<int:category_id>')
def category_view(category_id):
    """Страница просмотра конкретной категории со списком тем."""
    # 1. Запрашиваем из базы данные самой категории (имя, описание)
    category = TopicRepository.get_category(category_id)
    
    # Защита: если категории с таким ID нет в базе (например, ввели /category/999)
    if not category:
        abort(404) # Выдаем честную страницу "Не найдено"
        
    # 2. Получаем список всех тем, привязанных к этой категории
    topics_list = TopicRepository.get_topics_by_category(category_id)
    
    # 3. Берем точное живое время для ретро-часов в подвале
    now = datetime.now()
    
    # 4. Рендерим новый HTML-шаблон, передавая туда все данные
    return render_template(
        'forum/category.html',
        current_time=now,
        category=category,
        topics=topics_list
    )

@forum_bp.route('/category/<int:category_id>/create', methods=['GET', 'POST'])
def topic_create(category_id):
    """Создание новой темы в выбранной категории."""
    # 1. ЗАЩИТА: проверяем, авторизован ли пользователь
    author_id = session.get('user_id')
    if not author_id:
        return redirect('/login') # Если нет — отправляем авторизоваться

    # Получаем данные категории, чтобы красиво написать её имя в заголовке формы
    category = TopicRepository.get_category(category_id)
    if not category:
        abort(404)

    # Если пользователь просто кликнул по ссылке (GET-запрос) — показываем форму
    if request.method == 'GET':
        now = datetime.now()
        return render_template('forum/topic_create.html', current_time=now, category=category)

    # Если пользователь нажал кнопку "Отправить" (POST-запрос) — обрабатываем данные
    title = request.form.get('title')
    content = request.form.get('content')

    # Защита: проверка на пустые поля
    if not title or not content:
        now = datetime.now()
        return render_template(
            'forum/topic_create.html', 
            current_time=now, 
            category=category, 
            error="Заголовок темы и текст сообщения не могут быть пустыми!"
        )

    # 2. Вызываем наш метод-транзакцию из репозитория
    try:
        topic_id = TopicRepository.create_topic_with_first_post(
            category_id=category_id,
            author_id=author_id,
            title=title.strip(),
            content=content.strip()
        )
        # После успешного создания перенаправляем пользователя внутрь его новой темы
        # Пока страницы темы нет, временно редиректим обратно в категорию
        return redirect(f'/category/{category_id}')
    except Exception as e:
        now = datetime.now()
        return render_template(
            'forum/topic_create.html', 
            current_time=now, 
            category=category, 
            error="Произошла системная ошибка при сохранении темы. Попробуйте позже."
        )
    
@forum_bp.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def topic_view(topic_id):
    """Страница просмотра темы с сообщениями и формой быстрого ответа."""
    topic = PostRepository.get_topic(topic_id)
    if not topic:
        abort(404)

    # Если отправили форму быстрого ответа (POST)
    if request.method == 'POST':
        author_id = session.get('user_id')
        if not author_id:
            return redirect('/login')

        # Защита: если администратор закрыл тему, писать в нее нельзя
        if topic[3]: # topic[3] — это поле is_closed
            abort(403) # Доступ запрещен

        content = request.form.get('content')
        if content and content.strip():
            PostRepository.add_post(topic_id, author_id, content.strip())
        
        # Перезагружаем эту же страницу темы, чтобы увидеть свежий пост
        return redirect(f'/topic/{topic_id}')

    # Если это обычный просмотр (GET)
    posts_list = PostRepository.get_posts_by_topic(topic_id)
    now = datetime.now()
    
    return render_template(
        'forum/topic_detail.html',
        current_time=now,
        topic=topic,
        posts=posts_list
    )
