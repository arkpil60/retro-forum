from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repo import UserRepository

class AuthService:

    @classmethod
    def register_user(cls, username, password):

        if not username or not password:
            return {"success": False, "message": "Имя пользователя и пароль не могут быть пустыми!"}

        username = username.strip()

        hashed_password = generate_password_hash(password)

        try:
            UserRepository.create_user(username, hashed_password)
            return {"success": True, "message": "Регистрация успешна!"}
        except Exception as e:

            return {"success": False, "message": "Это имя пользователя уже занято!"}

    @classmethod
    def login_user(cls, username, password):

        if not username or not password:
            return {"success": False, "message": "Заполните все поля!"}

        user = UserRepository.find_by_username(username.strip())

        if not user:
            return {"success": False, "message": "Неверное имя пользователя или пароль!"}

        user_id, db_username, db_password_hash = user

        if check_password_hash(db_password_hash, password):
            return {"success": True, "user_id": user_id, "username": db_username}
        
        return {"success": False, "message": "Неверное имя пользователя или пароль!"}
