from flask import Flask, session
from config import Config
from app.services.time_shift import convert_to_retro
from app.repositories import BaseRepository

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    
    @app.context_processor
    def inject_retro_time():
        return dict(convert_to_retro=convert_to_retro)
        
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        BaseRepository.release_connection()

    @app.before_request
    def update_last_seen():
        # Внутри функции отступ равен строго 8 пробелам!
        if app.config.get('MAINTENANCE_MODE'):
            from flask import render_template
            return render_template('maintenance.html'), 503

        user_id = session.get('user_id')
        if user_id:
            conn = BaseRepository.get_db_connection()
            with conn.cursor() as cursor:
                sql = "UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = %s;"
                cursor.execute(sql, (user_id,))
                conn.commit()

        
    from app.routes.forum import forum_bp
    app.register_blueprint(forum_bp)
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
        
    return app
