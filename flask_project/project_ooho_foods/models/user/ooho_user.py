from project_ooho_foods.extensions import db
from passlib.hash import pbkdf2_sha256
import enum



class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"

#this is a db model for user 
class OohoUser(db.Model):
    __tablename__='user'

    STATUS_CHOICES =[(status.value, status.name) for status in StatusEnum]

    id = db.Column(db.String, primary_key=True)
    userName = db.Column(db.String, unique=True, nullable=False)
    Email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.active.value, nullable=False)
    Comment = db.relationship('Comment', backref='user', lazy=True)
    @staticmethod
    def set_password(password):
        return pbkdf2_sha256.hash(password)
    
    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def __repr__(self):
        return f'<UderData {self.userName}>'
    