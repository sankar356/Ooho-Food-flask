from flask import Blueprint

users = Blueprint('users', __name__)


from project_ooho_foods.users import route,routes
