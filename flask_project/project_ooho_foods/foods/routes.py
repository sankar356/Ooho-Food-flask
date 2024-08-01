#-------------------------------imports-------------------------------------------------------
from flask import *
from project_ooho_foods.foods import foods
from project_ooho_foods.extensions import csrf,db
from project_ooho_foods.models.foodfeedback import FeedBack
from project_ooho_foods.models.user.ooho_user import OohoUser
import uuid
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from project_ooho_foods.users.route import token_required
import logging,uuid
from datetime import datetime
#--------------------------------end imports------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@foods.route('/postfeedback',methods=['POST'])
@csrf.exempt
@token_required
def postfeedback(current_user):
    if request.is_json:
        data = request.get_json()
        comments = data.get('comments')
        food_id = data.get('food_id')
        rating = data.get('rating')
        
        # Ensure all required fields are provided
        if not all([comments, food_id, rating]):
            return jsonify({"error": "All fields are required"}), 400
        
        # Validate rating
        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        user = OohoUser.query.filter_by(id=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        feedback_id = str(uuid.uuid1())
        new_feedback = FeedBack(
            feedback_id=feedback_id,
            comments=comments,
            food_id=food_id,
            rating=rating,
            id=user.id,
            feedback_date=datetime.utcnow()
        )
        
        try:
            db.session.add(new_feedback)
            db.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error adding feedback: {e}", exc_info=True)
            db.session.rollback()
            return jsonify({"error": "Internal Server Error"}), 500

        return jsonify({
            "message": "Feedback added successfully",
            "feedback": {
                "feedback_id": new_feedback.feedback_id,
                "comments": new_feedback.comments,
                "feedback_date": new_feedback.feedback_date,
                "food_id": new_feedback.food_id,
                "rating": new_feedback.rating,
                "user": {
                    "id": user.id,
                    "userName": user.userName
                }
            }
        }), 201
    else:
        return jsonify({"error": "Request must be JSON"}), 400