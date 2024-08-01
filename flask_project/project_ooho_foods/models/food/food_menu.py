from project_ooho_foods.extensions import db
import enum

class StatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"



class FoodStatus(enum.Enum):
    available = 'available'
    not_available = 'not_available'

    
class Foods(db.Model):
    __tablename__ ='foods_data'

    food_id = db.Column(db.String, primary_key=True)
    food_name = db.Column(db.String, unique=True, nullable=False)
    food_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    food_status = db.Column(db.Enum(FoodStatus), default=FoodStatus.available.value, nullable=False)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.active.value, nullable=False)


    
