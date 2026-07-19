from app.repositories import BaseRepository

class ForumRepository(BaseRepository):
    """Репозиторий для работы со структурой форума (категории, статистика)."""

    @classmethod
    def get_all_categories(cls):
        """
        Вытягивает все категории и динамически подсчитывает 
        количество тем и сообщений внутри каждой из них.
        """
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            # Считаем темы напрямую через category_id, 
            # а сообщения — через связь постов с темами этой категории
            sql = """
                SELECT 
                    c.id, 
                    c.name, 
                    c.description,
                    (SELECT COUNT(*) FROM topics t WHERE t.category_id = c.id) as topic_count,
                    (SELECT COUNT(*) FROM posts p 
                     JOIN topics t ON p.topic_id = t.id 
                     WHERE t.category_id = c.id) as post_count
                FROM categories c
                ORDER BY c.id;
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @classmethod
    def get_forum_stats(cls):
        """Возвращает общее количество пользователей, тем и сообщений."""
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            # Считаем количество строк во всех трех таблицах за один проход
            sql = """
                SELECT 
                    (SELECT COUNT(*) FROM users) as users_count,
                    (SELECT COUNT(*) FROM topics) as topics_count,
                    (SELECT COUNT(*) FROM posts) as posts_count;
            """
            cursor.execute(sql)
            # fetchone() вернет один кортеж, например: (1, 0, 0)
            return cursor.fetchone()

    @classmethod
    def get_online_users(cls):
        """Возвращает список имен пользователей, активных последние 5 минут."""
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            # Выбираем имена пользователей, у которых last_seen старше текущего времени минус 5 минут
            sql = """
                SELECT username 
                FROM users 
                WHERE last_seen >= CURRENT_TIMESTAMP - INTERVAL '5 minutes'
                ORDER BY username;
            """
            cursor.execute(sql)
            # Извлекаем плоский список имен
            rows = cursor.fetchall()
            return [row[0] for row in rows]
