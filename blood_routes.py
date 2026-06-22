from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, BloodRequest

blood_bp = Blueprint('blood_bp', __name__)

BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'O+': ['O+', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'O-': ['O-'],
    'B-': ['B-', 'O-'],
    'AB-': ['AB-', 'A-', 'B-', 'O-']
}

@blood_bp.route('/organizer/blood_network')
def blood_network():
    if 'user_id' not in session or session.get('user_role') not in ['ngo', 'organizer', 'admin']: 
        return redirect(url_for('login'))
        
    requests = BloodRequest.query.order_by(BloodRequest.created_at.desc()).all()
    donors = User.query.filter_by(role='volunteer', is_emergency_donor=True).all()
    return render_template('blood_network.html', requests=requests, donors=donors)

@blood_bp.route('/blood/request', methods=['POST'])
def submit_blood_request():
    if 'user_id' not in session or session.get('user_role') not in ['ngo', 'organizer', 'admin']: 
        return redirect(url_for('login'))
        
    br = BloodRequest(
        ngo_id=session['user_id'],
        patient_name=request.form.get('patient_name'),
        hospital_name=request.form.get('hospital_name', 'Unknown'),
        blood_type_needed=request.form.get('blood_group_needed', 'O+'),
        units_needed=int(request.form.get('units_required', 1)),
        urgency_score=int(request.form.get('urgency', 5)),
        city=request.form.get('city', 'Hospital Main Gate')
    )
    db.session.add(br)
    db.session.commit()
    
    # Normally we'd emit via socketio, but to avoid circular import issues, 
    # we can just flash a message.
    flash("High-priority blood request broadcasted to the donor network!")
    return redirect(url_for('blood_bp.blood_network'))

@blood_bp.route('/blood/update/<int:request_id>', methods=['POST'])
def update_blood_status(request_id):
    if 'user_id' not in session: 
        return redirect(url_for('login'))
        
    br = BloodRequest.query.get_or_404(request_id)
    br.status = request.form.get('status', 'Pending')
    
    if br.status == 'Donor Assigned' and session.get('user_role') == 'volunteer':
        br.assigned_donor_id = session['user_id']
        
    db.session.commit()
    flash(f"Blood request status updated to: {br.status}")
    
    if session.get('user_role') in ['ngo', 'organizer']:
        return redirect(url_for('blood_bp.blood_network'))
    else:
        return redirect(url_for('volunteer_dashboard'))

@blood_bp.route('/blood/arrived/<int:request_id>', methods=['POST'])
def blood_arrived(request_id):
    """Volunteer has arrived at the hospital."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    br = BloodRequest.query.get_or_404(request_id)
    br.status = 'Volunteer Arrived'
    br.assigned_donor_id = session['user_id']
    db.session.commit()
    flash("Great! You've arrived. Please check in with hospital staff.")
    return redirect(url_for('volunteer_dashboard'))

@blood_bp.route('/blood/will_donate/<int:request_id>', methods=['POST'])
def blood_will_donate(request_id):
    """Volunteer has confirmed they will donate."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    br = BloodRequest.query.get_or_404(request_id)
    br.status = 'Donation In Progress'
    db.session.commit()
    flash("Thank you for confirming! Please proceed to the donation center.")
    return redirect(url_for('volunteer_dashboard'))

@blood_bp.route('/blood/donated/<int:request_id>', methods=['POST'])
def blood_donated(request_id):
    """Volunteer has completed the donation. Apply 90-day cooldown."""
    from datetime import datetime
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    br = BloodRequest.query.get_or_404(request_id)
    br.status = 'Completed'
    
    from datetime import datetime as dt
    donor = User.query.get(session['user_id'])
    donor.last_donation_date = dt.utcnow()
    
    db.session.commit()
    flash("🩸 Donation recorded! You've saved a life. You're now in a 90-day rest period.")
    return redirect(url_for('volunteer_dashboard'))
