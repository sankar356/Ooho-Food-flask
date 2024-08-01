from flask import Blueprint

admin = Blueprint('admin', __name__)


from project_ooho_foods.ooho_admin.admin import route