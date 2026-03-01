from flask import Blueprint, jsonify, request
from app import db
from app.models import Slot, User, Booking
from flasgger import swag_from

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/slots', methods=['GET'])
def get_slots():
    """
    Get all parking slots
    ---
    tags:
      - Slots
    responses:
      200:
        description: List of all slots
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              location:
                type: string
              price:
                type: integer
              is_occupied:
                type: boolean
    """
    slots = Slot.query.all()
    results = []
    for slot in slots:
        results.append({
            'id': slot.id,
            'location': slot.location,
            'price': slot.price,
            'is_occupied': slot.is_occupied,
            'owner_id': slot.owner_id
        })
    return jsonify(results)

@api_bp.route('/slots/<int:id>', methods=['GET'])
def get_slot(id):
    """
    Get a specific slot
    ---
    tags:
      - Slots
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Slot details
      404:
        description: Slot not found
    """
    slot = Slot.query.get(id)
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404
    
    return jsonify({
        'id': slot.id,
        'location': slot.location,
        'price': slot.price,
        'is_occupied': slot.is_occupied,
        'owner_id': slot.owner_id
    })

@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    Get user details (Wallet Balance)
    ---
    tags:
      - Users
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User details
      404:
        description: User not found
    """
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'id': user.id,
        'name': user.name,
        'role': user.role,
        'wallet_balance': user.wallet_balance
    })
