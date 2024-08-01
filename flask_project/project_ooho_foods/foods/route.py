#-------------------------------imports-------------------------------------------------------
from flask import *
from project_ooho_foods.foods import foods
from project_ooho_foods.extensions import csrf,db
from project_ooho_foods.models.food.food_menu import Foods, FoodStatus, StatusEnum
import uuid
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from project_ooho_foods.ooho_admin.admin.route import admin_required
#--------------------------------end imports------------------------------------------------------
#--------------------------------get and post------------------------------------------------------
@foods.route('/addfood',methods=['POST','GET'])
@csrf.exempt
@jwt_required()
@admin_required('admin','staff')
# @admin_required('staff')
def addFood():
    if request.method == 'POST':
        data = request.get_json()  # Call the method with parentheses
        if not data:
            return jsonify({"error": "invalid input"}), 400
        
        food_name = data.get('food_name')
        food_type = data.get('food_type')
        description = data.get('description')
        price = data.get('price')
        food_status = FoodStatus.available.value
        status = StatusEnum.active.value  

        if not all([food_name, food_type, description, price]):
            return jsonify({'error': 'Missing fields'}), 400
        
        food_id = str(uuid.uuid4())
        new_food = Foods(
            food_id=food_id,
            food_name=food_name,
            food_type=food_type,
            description=description,
            price=price,
            food_status=food_status,
            status=status
        )

        try:
            db.session.add(new_food)
            db.session.commit()
            return jsonify({
                'food_name': new_food.food_name,
                'food_type': new_food.food_type
            }), 201
        
        except SQLAlchemyError as s:
            db.session.rollback()
            return jsonify({"error": str(s)}), 500

    elif request.method == 'GET':
        try:
            # Query for foods with active status
            foods_list = Foods.query.filter_by(status=StatusEnum.active).all()
        
            if not foods_list:
                return jsonify({'data': 'No active foods found'}), 404
            
            food_list = [{
                'food_id': food.food_id,
                'food_name': food.food_name,
                'food_type': food.food_type,
                'description': food.description,
                'price': food.price,
                'food_status': food.food_status.value,
                'status': food.status.value
            } for food in foods_list]

            return jsonify({"data": food_list}), 200

        except SQLAlchemyError as e:
            return jsonify({'error': str(e)}), 500
        
#--------------------------------multiple method in food------------------------------------------------------

@foods.route('/update/<food_id>', methods=['PUT','DELETE','GET'])
@csrf.exempt
@jwt_required()
@admin_required('admin','staff')
def updatefood(food_id):
    food = Foods.query.filter_by(food_id=food_id, status=StatusEnum.active.value).first()
    if food is None:
        return jsonify({'data': 'User not found or not active'}), 404
    if request.method=='GET':
            
        food_list =[{
                    'food_id': food.food_id,
                    'food_name': food.food_name,
                    'food_type': food.food_type,
                    'description': food.description,
                    'price': food.price,
                    'food_status': food.food_status.value,
                    'status': food.status.value
                }]
        for food in food_list:
            food['status'] = str(food['status'])
        
        return jsonify({'data':food_list})
    elif request.method == 'PUT':
        data = request.get_json()

        if not data:
            return jsonify({"error":"invalid data"})
        food.food_name = data.get('food_name', food.food_name)
        food.food_type = data.get('food_type', food.food_type)
        food.description = data.get('description', food.description)
        food.price = data.get('price', food.price)

        try:
            db.session.commit()
            food_list = [{
                'food_id': food.food_id,
                'food_name': food.food_name,
                'food_type': food.food_type,
                'description': food.description,
                'price': food.price,
                'food_status': food.food_status.value,
                'status': food.status.value
            }]
            for food in food_list:
                food['status'] = str(food['status'])
            return jsonify({'data':food_list})
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    elif request.method == 'DELETE':
        try:
            food = Foods.query.filter_by(food_id=food_id, status=StatusEnum.active.value).first()
            if food is None:
                return jsonify({'data': 'User not found or not active'}), 404

            food.status = StatusEnum.inactive.value
            db.session.add(food)
            db.session.commit()
            return jsonify({'data': 'User status updated to delete'}), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
#---------------------------delete food-----------------------------------------------------------
@foods.route('/deletefood/<food_id>', methods=['DELETE'])
@csrf.exempt
@jwt_required()
@admin_required('admin')
def deleteFood(food_id):
    if request.method == 'DELETE':
        try:

            food = Foods.query.filter_by(food_id=food_id, status=StatusEnum.inactive.value).first()
            print(food)
            if food is None:
                return jsonify({'data': 'User not found or not active'}), 404

            food.status = StatusEnum.active.value
            db.session.add(food)
            db.session.commit()
            return jsonify({'data': 'User status updated to active'}), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
#-----------------------------get food by id---------------------------------------------------------
@foods.route('/foodavailablety/<food_id>', methods=['DELETE','PUT'])
@csrf.exempt
@jwt_required()
@admin_required('admin')
def availablefood(food_id):
        if request.method == 'DELETE':
            try:
                food = Foods.query.filter_by(food_id=food_id, food_status=FoodStatus.available.value).first()
                if food is None:
                    return jsonify({'data': 'User not found or not active'}), 404
                food.food_status = FoodStatus.not_available.value
                db.session.add(food)
                db.session.commit()
                return jsonify({'data': 'not_available'}), 200
            
            except SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
            
        elif request.method == 'PUT':
            try:
                food = Foods.query.filter_by(food_id=food_id, food_status=FoodStatus.not_available.value).first()
                if food is None:
                    return jsonify({'data': 'User not found or not active'}), 404
                food.food_status = FoodStatus.available.value
                db.session.add(food)
                db.session.commit()
                return jsonify({'data': 'available'}), 200
            

            except SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
#--------------------------------get all food------------------------------------------------------
@foods.route('/getfood',methods=['GET'])
@csrf.exempt
@jwt_required()
def getfoods():
        try:
            # Query for foods with active status
            foods_list = Foods.query.filter_by(status=StatusEnum.active).all()
        
            if not foods_list:
                return jsonify({'data': 'No active foods found'}), 404
            
            food_list = [{
                'food_id': food.food_id,
                'food_name': food.food_name,
                'food_type': food.food_type,
                'description': food.description,
                'price': food.price,
                'food_status': food.food_status.value,
                'status': food.status.value
            } for food in foods_list]

            return jsonify({"data": food_list}), 200

        except SQLAlchemyError as e:
            return jsonify({'error': str(e)}), 500

#--------------------------------------------------------------------------------------


 
#this delete method for delete data from table

#def deletefood():
#     try:
#         food_item = Foods.query.get(food_id)
        
#         if not food_item:
#             return jsonify({'error': 'Food item not found'}), 404
        
#         db.session.delete(food_item)
#         db.session.commit()
#         return jsonify({'message': 'Food item deleted successfully'}), 200
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
    



   
