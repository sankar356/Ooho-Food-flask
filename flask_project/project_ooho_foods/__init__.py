from flask import Flask
from config import Config
from project_ooho_foods.extensions import db, csrf, jwt
from flask_wtf import CSRFProtect


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    csrf.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    from project_ooho_foods.users import users
    app.register_blueprint(users, url_prefix='/user')

    from project_ooho_foods.foods import foods
    app.register_blueprint(foods, url_prefix='/foods')

    from project_ooho_foods.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from project_ooho_foods.ooho_admin.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    # from project_ooho_foods.main import basic
    # app.register_blueprint(basic, url_prefix='/basic')
    # # jwt.init_app(app)
    # from app.auth import  auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')


    

    return app