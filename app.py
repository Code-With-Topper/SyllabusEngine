from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from dotenv import load_dotenv
from extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    from database.models import User
    return User.query.get(int(user_id))

def create_app():
    from dotenv import load_dotenv
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.subjects import subjects_bp
    from routes.upload import upload_bp
    from routes.study_plan import study_plan_bp
    from routes.assistant import assistant_bp
    from routes.calendar import calendar_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(study_plan_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(calendar_bp)

    app.register_blueprint(admin_bp)

    # Initialize database and seed admin
    with app.app_context():
        db.create_all()
        
        from database.models import User
        admin_email = "soumya@admin.com"
        admin_password = "Soumya@290806"
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                name="Soumya",
                role='admin',
                is_admin=True
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ Default admin created: {admin_email} / {admin_password}")
        else:
            print(f"ℹ️ Admin already exists: {admin_email}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
