from app.repositories import BaseRepository

class TopicRepository(BaseRepository):
    """Репозиторий для работы с темами форума в PostgreSQL."""

    @classmethod
    def get_category(cls, category_id):
        """Возвращает данные конкретной категории (id, name, description)."""
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT id, name, description FROM categories WHERE id = %s;"
            cursor.execute(sql, (category_id,))
            return cursor.fetchone()

    @classmethod
    def get_topics_by_category(cls, category_id):
        """
        Вытягивает все темы из выбранной категории.
        Склеивает (JOIN) их с таблицей пользователей, чтобы узнать имя автора.
        """
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            # Используем LEFT JOIN: если автор удалился (author_id станет NULL), 
            # тема все равно выведется, а вместо имени автора вернется None.
            sql = """
                SELECT 
                    t.id, 
                    t.title, 
                    t.created_at, 
                    t.is_closed, 
                    u.username as author_name
                FROM topics t
                LEFT JOIN users u ON t.author_id = u.id
                WHERE t.category_id = %s
                ORDER BY t.id DESC;
            """
            cursor.execute(sql, (category_id,))
            return cursor.fetchall()

    @classmethod
    def create_topic_with_first_post(cls, category_id, author_id, title, content):
        """
        Создает тему и первое сообщение внутри нее в единой транзакции.
        """
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            try:
                # 1. Создаем саму тему в таблице topics (используем твой author_id!)
                sql_topic = """
                    INSERT INTO topics (title, category_id, author_id) 
                    VALUES (%s, %s, %s) 
                    RETURNING id;
                """
                cursor.execute(sql_topic, (title, category_id, author_id))
                # Забираем ID только что созданной темы
                topic_id = cursor.fetchone()[0]

                # 2. Создаем первый пост этой темы в таблице posts
                sql_post = """
                    INSERT INTO posts (topic_id, author_id, content) 
                    VALUES (%s, %s, %s);
                """
                cursor.execute(sql_post, (topic_id, author_id, content))

                # 3. Фиксируем транзакцию: обе записи одновременно сохраняются на диск СУБД
                conn.commit()
                return topic_id
            except Exception as e:
                # Если что-то пошло не так (например, оборвалась связь), отменяем изменения
                conn.rollback()
                raise e
