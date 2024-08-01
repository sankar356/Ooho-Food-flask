#-----------------------imports---------------------------------------------------------------
from flask import *
from project_ooho_foods.ooho_admin.admin import admin
from project_ooho_foods.extensions import csrf,db,foo,jwt
from project_ooho_foods.ooho_admin.model.adminModel import Roles,AddUserRole
from project_ooho_foods.models.user.ooho_user import OohoUser
import uuid
from functools import wraps
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity, get_jwt
from sqlalchemy.orm.exc import NoResultFound
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
#-------------------------end imports-------------------------------------------------------------


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def adduser_role_details(id):
    staff_roles = db.session.query(Roles).filter(Roles.role_name == "staff").all()
    role_ids = [role.role_id for role in staff_roles]

    try:
        for role_id in role_ids:
            new_role = AddUserRole(id=id, role_id=role_id)
            db.session.add(new_role)
        db.session.commit()
        return 201
    except SQLAlchemyError as e:
        logger.error(f"Error assigning roles: {e}")
        db.session.rollback()
        return 500
#--------------------------------------------------------------------------------------
app.secret_key = foo
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            decoded_token = get_jwt()
        except ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 403
        except Exception as e:
            return jsonify({'error': 'Token is missing or invalid'}), 403
        
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated
#----------------------------------------------------------------------------------
# this is for single access

# def admin_required(name):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             try:
#                 current_user_id = get_jwt_identity()
#                 user_role = db.session.query(AddUserRole).join(Roles).filter(
#                     AddUserRole.id == current_user_id,
#                     Roles.role_name == name
#                 ).first()
#                 if user_role is None:
#                     return jsonify({"error": "Forbidden"}), 403
#                 return f(*args, **kwargs)
#             except NoResultFound:
#                 return jsonify({"error": "Forbidden"}), 403
#             except Exception as e:
#                 return jsonify({"error": str(e)}), 500
#         return decorated_function
#     return decorator
#--------------------------------------------------------------------------------------

def admin_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                
                user_role = db.session.query(AddUserRole).join(Roles).filter(
                    AddUserRole.id == current_user_id,
                    Roles.role_name.in_(roles)
                ).first()
                
                if user_role is None:
                    return jsonify({"error": "Forbidden"}), 403
                
                return f(*args, **kwargs)
            except NoResultFound:
                return jsonify({"error": "Forbidden"}), 403
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return decorated_function
    return decorator
#--------------------------------------------------------------------------------------
@admin.route('/adminenrole',methods=['GET','POST'])
@csrf.exempt
@jwt_required()
@admin_required('admin')
def add_new_user():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid input'}), 400

        userName = data.get('userName')
        Email = data.get('Email')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')

        if not all([userName, Email, password, firstName, lastName]):
            return jsonify({'error': 'Missing fields'}), 400

        # Check if email already exists
        existing_user = db.session.query(OohoUser).filter(OohoUser.Email == Email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        id = str(uuid.uuid4())
        hashed_password = OohoUser.set_password(password)
        new_user = OohoUser(id=id, userName=userName, password=hashed_password, Email=Email, firstName=firstName, lastName=lastName)

        try:
            db.session.add(new_user)
            db.session.commit()
            role_assignment_status = adduser_role_details(id)
            if role_assignment_status == 500:
                return jsonify({'error': 'Error assigning roles'}), 500
            return jsonify({'user_id': new_user.id, 'userName': new_user.userName}), 201
        except IntegrityError as e:
            logger.error(f"IntegrityError: {e}")
            db.session.rollback()
            return jsonify({'error': 'Duplicate entry'}), 400
        except SQLAlchemyError as e:
            logger.error(f"Error adding new user: {e}")
            db.session.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500
        
    elif request.method == 'GET':
        sadmin = OohoUser.query.all()
        
        admin_list = [{
            'id': admins.id,
            'userName': admins.userName,
            'Email': admins.Email,
            'firstName': admins.firstName,
            'lastName': admins.lastName,
            'status': admins.status
        } for admins in sadmin]

        for user_data in admin_list:
            user_data['status'] = str(user_data['status'])

        return jsonify({"data": admin_list}), 200
    else:
        return 'Method Not Allowed', 405
    
#--------------------------------------------------------------------------------------
@admin.route('/adminviewbyadmin',methods=['GET'])
# @jwt_required()
# @admin_required('admin')
@csrf.exempt
@token_required
def getbyid(current_user):
    # user =OohoUser.query.get(id)
    user = OohoUser.query.filter_by(id=current_user).first()
    users_list =[{
          "id":user.id,
          "userName":user.userName,
          "Email":user.Email,
          "password":user.password,
          "firstName":user.firstName,
          "lastName":user.lastName,
          "status" :user.status       
     }]
    for users in users_list:
        users['status'] = str(users['status'])
    
    return jsonify({'data':users_list})
#--------------------------------------------------------------------------------------
