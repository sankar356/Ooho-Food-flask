from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_jwt_extended import JWTManager
import secrets

foo = secrets.token_urlsafe(16)
db = SQLAlchemy()
csrf = CSRFProtect()
jwt = JWTManager()
blacklist = set()