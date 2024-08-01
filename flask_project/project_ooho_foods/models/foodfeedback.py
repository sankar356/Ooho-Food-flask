from project_ooho_foods.extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class FeedBack(db.Model):
    __tablename__ = 'food_feedback'
    
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(90), db.ForeignKey('user.id'), nullable=False)
    food_id = db.Column(db.String(90), db.ForeignKey('foods_data.food_id'), nullable=False)
    rating = db.Column(db.Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comments = db.Column(db.Text)
    feedback_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FeedBack {self.feedback_id}>'