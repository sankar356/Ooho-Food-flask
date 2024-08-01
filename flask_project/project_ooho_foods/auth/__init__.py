from flask import Blueprint

auth = Blueprint('auth', __name__)


from project_ooho_foods.auth import route
