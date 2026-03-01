import os
import uuid
from flask import Blueprint, render_template, request, redirect, flash, session, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Slot, ParkingLot
from app.socket_events import broadcast_slot_update

owner_bp = Blueprint('owner', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@owner_bp.route('/owner_dashboard')
def dashboard():
    if 'user_id' not in session or session['role'] != 'Owner':
        return redirect('/login')
    user = User.query.get(session['user_id'])
    session['wallet'] = user.wallet_balance
    slots = Slot.query.filter_by(owner_id=user.id).all()
    parking_lots = ParkingLot.query.filter_by(owner_id=user.id).all()
    return render_template('dashboard_owner.html', slots=slots, earnings=user.wallet_balance, parking_lots=parking_lots)


@owner_bp.route('/add_slot', methods=['POST'])
def add_slot():
    if 'user_id' not in session:
        return redirect('/login')
    location = request.form['location']
    price = request.form['price']
    new_slot = Slot(owner_id=session['user_id'], location=location, price=price)
    db.session.add(new_slot)
    db.session.commit()
    broadcast_slot_update()
    flash('Slot added!')
    return redirect('/owner_dashboard')


@owner_bp.route('/add_parking', methods=['POST'])
def add_parking():
    if 'user_id' not in session or session['role'] != 'Owner':
        return redirect('/login')

    name = request.form.get('parking_name', '').strip()
    city = request.form.get('city', '').strip()
    full_address = request.form.get('full_address', '').strip()
    # legacy location field: combine city + address for backwards compat
    location = f"{full_address}, {city}".strip(', ') if (full_address or city) else request.form.get('parking_location', '').strip()

    try:
        lat = float(request.form.get('latitude', 0))
        lng = float(request.form.get('longitude', 0))
        available_slots = int(request.form.get('available_slots', 1))
        price_raw = request.form.get('price', '').strip()
        price = int(price_raw) if price_raw else None
    except ValueError:
        flash('Please enter valid numbers for latitude, longitude, slots, and price.')
        return redirect('/owner_dashboard')

    vehicle_type = request.form.get('vehicle_type', 'car')

    # Handle image upload
    image_filename = None
    file = request.files.get('parking_image')
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        image_filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

    lot = ParkingLot(
        owner_id=session['user_id'],
        name=name,
        city=city,
        full_address=full_address,
        location=location,
        latitude=lat,
        longitude=lng,
        available_slots=available_slots,
        vehicle_type=vehicle_type,
        price=price,
        image_filename=image_filename
    )
    db.session.add(lot)
    db.session.commit()

    flash(f'🎉 "{name}" has been listed successfully!')
    return redirect('/owner_dashboard')


@owner_bp.route('/api/parking_lots')
def api_parking_lots():
    """JSON endpoint for Leaflet map markers. Supports ?city=<name> filter."""
    city_q = request.args.get('city', '').strip()
    query = ParkingLot.query
    if city_q:
        query = query.filter(ParkingLot.city.ilike(f'%{city_q}%'))
    lots = query.all()
    data = [{
        'id': lot.id,
        'name': lot.name,
        'city': lot.city or '',
        'location': lot.location,
        'full_address': lot.full_address or lot.location,
        'lat': lot.latitude,
        'lng': lot.longitude,
        'available_slots': lot.available_slots,
        'vehicle_type': lot.vehicle_type,
        'price': lot.price,
        'image': lot.image_filename or '',
    } for lot in lots]
    return jsonify(data)
