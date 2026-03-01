from flask_socketio import emit
from app import socketio

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Event: When a slot is modified (booked/freed/added)
# We will emit 'update_slots' to ALL clients so they see it instantly
def broadcast_slot_update():
    socketio.emit('update_slots', {'status': 'refresh_needed'})
