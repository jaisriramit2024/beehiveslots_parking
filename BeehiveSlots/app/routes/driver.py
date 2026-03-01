from flask import Blueprint, render_template, request, redirect, flash, session, jsonify
from app import db
from app.models import User, Slot, Booking, ParkingLot, ParkingLotBooking
from app.socket_events import broadcast_slot_update
from datetime import datetime, timezone

driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/driver_dashboard')
def dashboard():
    if 'user_id' not in session or session['role'] != 'Driver':
        return redirect('/login')
        
    user = User.query.get(session['user_id'])
    session['wallet'] = user.wallet_balance
    
    all_slots = Slot.query.all()
    
    # Active booking
    active_booking = Booking.query.filter_by(user_id=user.id, status='Active').first()
    
    return render_template('dashboard_driver.html', all_slots=all_slots, active_booking=active_booking)

@driver_bp.route('/add_money', methods=['POST'])
def add_money():
    if 'user_id' not in session: return redirect('/login')
    
    amount = int(request.form['amount'])
    user = User.query.get(session['user_id'])
    user.wallet_balance += amount
    db.session.commit()
    
    flash(f"Added ₹{amount} to wallet!")
    return redirect('/driver_dashboard')

@driver_bp.route('/book_slot', methods=['POST'])
def book_slot():
    if 'user_id' not in session: return redirect('/login')
    
    slot_id = request.form['slot_id']
    user_id = session['user_id']
    
    # Check existing booking
    if Booking.query.filter_by(user_id=user_id, status='Active').first():
        flash("You already have an active booking!")
        return redirect('/driver_dashboard')
        
    slot = Slot.query.get(slot_id)
    if slot.is_occupied:
        flash("Slot already occupied!")
        return redirect('/driver_dashboard')
        
    # Book it
    slot.is_occupied = True
    booking = Booking(user_id=user_id, slot_id=slot_id, start_time=datetime.utcnow())
    db.session.add(booking)
    db.session.commit()
    
    broadcast_slot_update()
    
    flash("Slot booked!")
    return redirect('/driver_dashboard')

@driver_bp.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session: return redirect('/login')
    
    booking_id = request.form['booking_id']
    booking = Booking.query.get(booking_id)
    slot = Slot.query.get(booking.slot_id)
    driver = User.query.get(session['user_id'])
    owner = User.query.get(slot.owner_id)
    
    # Calculate Cost
    end_time = datetime.utcnow()
    duration = (end_time - booking.start_time).total_seconds() / 3600
    hours = max(1, int(duration) + (1 if duration % 1 > 0 else 0))
    cost = hours * slot.price
    
    if driver.wallet_balance < cost:
        flash(f"Insufficient funds! Cost: \u20b9{cost}. Wallet: \u20b9{driver.wallet_balance}.")
        return redirect('/driver_dashboard')
        
    # Transaction
    driver.wallet_balance -= cost
    owner.wallet_balance += cost
    
    booking.end_time = end_time
    booking.status = 'Completed'
    booking.total_cost = cost
    
    slot.is_occupied = False
    
    db.session.commit()
    broadcast_slot_update()
    
    flash(f"Checked out! Paid \u20b9{cost}.")
    return redirect('/driver_dashboard')


@driver_bp.route('/parking/<int:lot_id>')
def parking_detail(lot_id):
    """Parking lot detail page for parkers."""
    lot = ParkingLot.query.get_or_404(lot_id)
    return render_template('parking_detail.html', lot=lot)


@driver_bp.route('/book_parking/<int:lot_id>', methods=['GET'])
def book_parking(lot_id):
    """Payment page: choose duration and confirm payment."""
    if 'user_id' not in session:
        flash('Please log in to book a slot.')
        return redirect('/login')
    lot = ParkingLot.query.get_or_404(lot_id)
    user = User.query.get(session['user_id'])
    return render_template('payment.html', lot=lot, user=user)


@driver_bp.route('/confirm_booking/<int:lot_id>', methods=['POST'])
def confirm_booking(lot_id):
    """Process payment from wallet and create booking."""
    if 'user_id' not in session:
        return redirect('/login')

    lot = ParkingLot.query.get_or_404(lot_id)
    user = User.query.get(session['user_id'])

    try:
        duration = int(request.form.get('duration', 1))
        duration = max(1, min(duration, 24))  # clamp 1-24 hrs
    except ValueError:
        duration = 1

    price_per_hour = lot.price or 0
    total = price_per_hour * duration

    # Wallet check
    if user.wallet_balance < total:
        flash(f'Insufficient wallet balance. You need ₹{total} but have ₹{user.wallet_balance}.')
        return redirect(f'/book_parking/{lot_id}')

    if lot.available_slots <= 0:
        flash('Sorry, no slots are available right now.')
        return redirect(f'/parking/{lot_id}')

    # Deduct wallet & decrement slots
    user.wallet_balance -= total
    lot.available_slots -= 1

    # Owner earns money
    owner = User.query.get(lot.owner_id)
    if owner:
        owner.wallet_balance += total

    # Create booking record
    booking = ParkingLotBooking(
        user_id=user.id,
        lot_id=lot.id,
        duration_hours=duration,
        amount_paid=total,
        booked_at=datetime.utcnow(),
        status='Confirmed'
    )
    db.session.add(booking)
    db.session.commit()

    # Update session wallet
    session['wallet'] = user.wallet_balance

    return redirect(f'/ticket/{booking.id}')


@driver_bp.route('/ticket/<int:booking_id>')
def ticket(booking_id):
    """Booking confirmation ticket page."""
    if 'user_id' not in session:
        return redirect('/login')
    booking = ParkingLotBooking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        flash('Access denied.')
        return redirect('/')
    return render_template('ticket.html', booking=booking)
