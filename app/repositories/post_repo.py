from app.repositories import BaseRepository

class PostRepository(BaseRepository):
    """Репозиторий для работы с сообщениями (posts) в PostgreSQL."""

    @classmethod
    def get_topic(cls, topic_id):
        """Возвращает данные самой темы (id, title, category_id, is_closed)."""
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT id, title, category_id, is_closed FROM topics WHERE id = %s;"
            cursor.execute(sql, (topic_id,))
            return cursor.fetchone()

    @classmethod
    def get_posts_by_topic(cls, topic_id):
        """
        Вытягивает все сообщения из темы по порядку их создания.
        Склеивает с users, чтобы вытащить имя автора поста.
        """
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    p.id, 
                    p.content, 
                    p.created_at, 
                    u.username as author_name
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.topic_id = %s
                ORDER BY p.id ASC; -- Строго по порядку (вайб старого чата)
            """
            cursor.execute(sql, (topic_id,))
            return cursor.fetchall()

    @classmethod
    def add_post(cls, topic_id, author_id, content):
        """Добавляет новое сообщение (быстрый ответ) в тему."""
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO posts (topic_id, author_id, content) 
                VALUES (%s, %s, %s);
            """
            cursor.execute(sql, (topic_id, author_id, content))
            conn.commit()
