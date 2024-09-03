from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes import auth, staff, manager, admin, main
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(main.bp)
    app.register_blueprint(staff.bp, url_prefix='/staff')
    app.register_blueprint(manager.bp)
    # app.register_blueprint(admin.bp)

    return app
