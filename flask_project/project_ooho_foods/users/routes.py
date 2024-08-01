from flask import *
from project_ooho_foods.users import users
from project_ooho_foods.users.route import token_required
from project_ooho_foods.extensions import csrf,jwt,db
from project_ooho_foods.models.user.ooho_user import OohoUser
from project_ooho_foods.models.comment import Comment
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
import logging,uuid
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# from project_ooho_foods.ooho_admin.admin.route import admin_required


# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'Authorization' in request.headers:
#             token = request.headers['Authorization'].split(" ")[1]  # Format: Bearer <Token>

#         if not token:
#             return jsonify({'message': 'Token is missing'}), 401

#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#             current_user = OohoUser.query.get(data['user_id'])
#         except Exception as e:
#             return jsonify({'message': str(e)}), 401

#         return f(current_user, *args, **kwargs)

    # return decorated
def about_us():
    pass
# this riute heps to user to add feedback
@users.route('/comments', methods=['POST'])
@csrf.exempt
@jwt_required()
@token_required
def add_comment(current_user):
    if request.is_json:
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({"error": "Content is required"}), 400

        user = OohoUser.query.filter_by(id=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        comment_id = str(uuid.uuid1())
        new_comment = Comment(
            comment_id =comment_id,
            content=content,
            id=user.id
        )
        
        try:
            db.session.add(new_comment)
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error adding comment: {e}", exc_info=True)
            db.session.rollback()
            return jsonify({"error": "Internal Server Error"}), 500

        return jsonify({
            "message": "Comment added successfully",
            "comment": {
                "id": new_comment.comment_id,
                "content": new_comment.content,
                "created_at": new_comment.created_at,
                "user": {
                    "id": user.id,
                    "userName": user.userName
                }
            }
        }), 201
    else:
        return jsonify({"error": "Request must be JSON"}), 400
    
# this route helps to get all feedback 
@users.route('/getcomments', methods=['GET'])
@csrf.exempt
@jwt_required()
def get_comments():
    Comments = Comment.query.all()
    comments_list = []
    
    for comment in Comments:
        comment_data = {
            "comment_id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "user_id": comment.id,
            "username": comment.user.userName
        }
        comments_list.append(comment_data)
    
    return jsonify(comments_list)

def user_offers():
    pass
