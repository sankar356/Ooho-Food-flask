from project_ooho_foods.extensions import db
from passlib.hash import pbkdf2_sha256
import enum


# class StatusEnum(enum.Enum):
#     active = "active"
#     inactive = "inactive"

# class OohoAdmin(db.Model):
#     __tablename__='user'

#     id = db.Column(db.String, primary_key=True)
#     userName = db.Column(db.String, unique=True, nullable=False)
#     Email = db.Column(db.String, unique=True, nullable=False)
#     password = db.Column(db.String, nullable=False)
#     firstName = db.Column(db.String, nullable=False)
#     lastName = db.Column(db.String, nullable=False)
#     status = db.Column(db.Enum(StatusEnum), default=StatusEnum.active.value, nullable=False)
#     @staticmethod
#     def set_password(password):
#         return pbkdf2_sha256.hash(password)
    
#     def check_password(self, password):
#         return pbkdf2_sha256.verify(password, self.password)

#     def __repr__(self):
#         return f'<UderData {self.userName}>'
    
    # table for roles
class Roles(db.Model):
     __tablename__ = 'roles'

     role_id = db.Column(db.String, primary_key=True)
     role_name = db.Column(db.String())

     def __repr__(self):
        return f'<Roles {self.role_name}>'

#hear use a model class for user_role_details
class AddUserRole(db.Model):
     __tablename__ = 'role_user_table'

     user_role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     role_id = db.Column(db.String, db.ForeignKey('roles.role_id'))
     id = db.Column(db.String, db.ForeignKey('user.id'))

     def __repr__(self):
        return f'<AddUserRole {self.id}>'