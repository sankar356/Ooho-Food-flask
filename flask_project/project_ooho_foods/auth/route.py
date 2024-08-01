from flask import *
from project_ooho_foods.auth import auth
from project_ooho_foods.extensions import csrf, blacklist
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from project_ooho_foods.models.user.ooho_user import OohoUser
# # from project_ooho_foods.ooho_admin.model import none

@auth.route('/login',methods =['POST'])
@csrf.exempt
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid input'}), 400

    Email = data.get('Email')
    password = data.get('password')

    if not all([Email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    user = OohoUser.query.filter_by(Email=Email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'message': 'Login success', 'userName': user.userName, 'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    
@auth.route('/logout',methods=['POST'])
@csrf.exempt
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200