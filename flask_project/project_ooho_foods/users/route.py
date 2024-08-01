from flask import *
from project_ooho_foods.users import users
from project_ooho_foods.extensions import csrf, db, foo, jwt
from project_ooho_foods.models.user.ooho_user import StatusEnum, OohoUser
from project_ooho_foods.ooho_admin.model.adminModel import Roles,AddUserRole
import uuid
from jwt import ExpiredSignatureError, InvalidTokenError
from functools import wraps
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity, get_jwt
from project_ooho_foods.ooho_admin.admin.route import admin_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def adduser_role_details(id):
    staff_roles = db.session.query(Roles).filter(Roles.role_name == "user").all()
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

app.secret_key = foo
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         if token:
#             if token.startswith('Bearer '):
#                 token = token[len('Bearer '):]  # Remove 'Bearer ' prefix
#         if not token:
#             return jsonify({'error': 'Token is missing'}), 403
#         try:
#             decoded_token = jwt.decode(token, config['secret_key'], algorithms=["HS256"])
#             request.decoded_token = decoded_token  # Optionally attach to request context
#         except jwt.ExpiredSignatureError:
#             return jsonify({'error': 'Token has expired'}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({'error': 'Token is invalid'}), 403
#         return f(*args, **kwargs)
#     return decorated

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


#this route helps to register user
@users.route('/userregist',methods=['POST'])
@csrf.exempt
def addUser():
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

        id = str(uuid.uuid4())  # Generate a new unique ID
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
# this route helps to get alluser records
@users.route('/getalluser',methods=['GET'])
@csrf.exempt
@jwt_required()
@admin_required('admin')
def get_active_users():
    try:
        # Query for users with active status
        users = OohoUser.query.filter_by(status=StatusEnum.active.value).all()
        
        if not users:
            return jsonify({'data': 'No active users found'}), 404

        # Serialize the user data
        user_list = [{
            'id': user.id,
            'userName': user.userName,
            'Email': user.Email,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'status': user.status
        } for user in users]

        for user_data in user_list:
            user_data['status'] = str(user_data['status'])

        return jsonify({"data": user_list}), 200

    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
# in this route helps to get user data by id
@users.route('/getuserbyid/',methods=['GET'])
@csrf.exempt
@token_required
def getbyid(current_user):
    user =OohoUser.query.get(id)
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
#this route can access by admin and using this route help to remove userdata
@users.route('/deleteuser/<id>',methods=['DELETE'])
@csrf.exempt     
@jwt_required()
@admin_required('admin')
def delete_user(id):
    try:
        user = OohoUser.query.filter_by(id=id, status=StatusEnum.active.value).first()
        if user is None:
            return jsonify({'data': 'User not found or not active'}), 404

        user.status = StatusEnum.inactive.value
        db.session.add(user)
        db.session.commit()
        return jsonify({'data': 'User status updated to delete'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
# in this route user can update thair value
@users.route('/updateData/<id>',methods=['PUT'])
@csrf.exempt
def updateData(id):
    user = OohoUser.query.filter_by(id=id, status=StatusEnum.active.value).first()
    if user is None:
        return jsonify({'data': 'User not found or not active'}), 404
    
    if request.method=='PUT':
        data = request.get_json()

        if not data:
            return jsonify({"error":"invalid data"})
        user.userName = data.get('userName', user.userName)
        user.Email = data.get('Email', user.Email)
        user.password = data.get('password', user.password)
        user.firstName = data.get('firstName', user.firstName)
        user.lastName = data.get('lastName', user.lastName)

        try:
            db.session.commit()
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
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
# this route helps to active for deactive user
@users.route('/changeuseractive/<id>',methods=['DELETE'])
@csrf.exempt
@jwt_required()
@admin_required('admin')
def deleteFood(id):
    if request.method == 'DELETE':
        try:
            user = OohoUser.query.filter_by(id=id, status=StatusEnum.inactive.value).first()
            print(user)
            if user is None:
                return jsonify({'data': 'User not found or not active'}), 404

            user.status = StatusEnum.active.value
            db.session.add(user)
            db.session.commit()
            return jsonify({'data': 'User status updated to active'}), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
@users.route('/deleteuserbyuser',methods=['DELETE'])
@csrf.exempt
@token_required
# @jwt_required()
# @admin_required('admin')
def deleteuser(current_user):
    if request.method == 'DELETE':
        try:
            user = OohoUser.query.filter_by(id=current_user).first()
            print(user)
            if user is None:
                return jsonify({'data': 'User not found or not active'}), 404

            user.status = StatusEnum.inactive.value
            db.session.add(user)
            db.session.commit()
            return jsonify({'data': 'User deleted'}), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500