from project_ooho_foods.extensions import db
from datetime import datetime
import enum



# this is a model foe comment feedback
class Comment(db.Model):
    __tablename__='comment'
    comment_id = db.Column(db.String, primary_key=True)
    content =db.Column(db.String)
    created_at =db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    id =db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f'<Comment {self.id}>'