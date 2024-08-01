from flask import Blueprint

foods = Blueprint('foods', __name__)


from project_ooho_foods.foods import route, routes
