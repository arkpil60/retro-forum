from app.repositories import BaseRepository

class UserRepository(BaseRepository):

    @classmethod
    def create_user(cls, username, password_hash):

        conn = cls.get_db_connection()

        with conn.cursor() as cursor:

            sql = """
                INSERT INTO users (username, password_hash) 
                VALUES (%s, %s) 
                RETURNING id;
            """
            cursor.execute(sql, (username, password_hash))
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id

    @classmethod
    def find_by_username(cls, username):
        conn = cls.get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT id, username, password_hash FROM users WHERE username = %s;"
            cursor.execute(sql, (username,))

            return cursor.fetchone()
