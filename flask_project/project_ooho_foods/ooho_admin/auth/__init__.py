from flask import Blueprint

adminauth = Blueprint('adminauth', __name__)


from project_ooho_foods.ooho_admin.auth import route