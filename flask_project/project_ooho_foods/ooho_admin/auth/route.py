from flask import *
from project_ooho_foods.ooho_admin.auth import adminauth
from project_ooho_foods.extensions import csrf, db
from project_ooho_foods.models.user import OohoUser
import uuid
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required