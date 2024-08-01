from flask import *
from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from project_ooho_foods.ooho_admin.model.adminModel import Roles,AddUserRole
from project_ooho_foods.extensions import csrf, db,jwt,foo




app.secret_key = foo
def token_required(f):
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'token is missing'}), 403
        try:
            jwt.decode(token, app.config['secret_key'], algorithms="HS256")
        except Exception as error:
            return jsonify({'error': 'token is invalid/expired'})
        return f(*args, **kwargs)
    return decorated



def admin_required(name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user_role = db.session.query(AddUserRole).join(Roles).filter(
                    AddUserRole.user_id == current_user_id,
                    Roles.role_name == name
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