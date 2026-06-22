from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from models import db, User, MissingPersonCase, Sighting, Task
from datetime import datetime
import io, csv

raksha_bp = Blueprint('raksha_bp', __name__)

@raksha_bp.route('/raksha/new', methods=['GET', 'POST'])
def raksha_forensic_form():
    if 'user_id' not in session or session.get('user_role') not in ['ngo', 'organizer', 'admin']: 
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        case = MissingPersonCase(
            organizer_id=session['user_id'],
            name=request.form.get('name'),
            nickname=request.form.get('nickname'),
            age=request.form.get('age'),
            gender=request.form.get('gender'),
            location_last_seen=request.form.get('location_last_seen'),
            latitude=request.form.get('latitude'),
            longitude=request.form.get('longitude'),
            distinctive_features=request.form.get('distinctive_features'),
            clothing_last_seen=request.form.get('clothing_last_seen')
        )
        
        # Handle file uploads
        import os
        from werkzeug.utils import secure_filename
        
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        def save_file(file_obj):
            if file_obj and file_obj.filename:
                filename = secure_filename(file_obj.filename)
                # To prevent collisions, prepend timestamp
                timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S_')
                filename = timestamp + filename
                path = os.path.join(upload_folder, filename)
                file_obj.save(path)
                return '/' + path.replace('\\', '/')
            return None

        case.photo_url = save_file(request.files.get('child_photo')) or save_file(request.files.get('photo'))
        case.body_photo_url = save_file(request.files.get('body_photo'))
        case.family_photo_url = save_file(request.files.get('family_photo'))
        
        db.session.add(case)
        db.session.commit()
        
        # We can flash instead of using socketio directly here to avoid circular imports.
        flash("RAAKSHA Search Mission Broadcasted Successfully!")
        return redirect(url_for('organizer_dashboard'))
        
    return render_template('raksha_forensic_form.html')

@raksha_bp.route('/raksha/case/<int:case_id>')
def view_case(case_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    case = MissingPersonCase.query.get_or_404(case_id)
    return render_template('view_case.html', case=case, user=user)

@raksha_bp.route('/raksha/sighting/<int:case_id>', methods=['GET', 'POST'])
def report_sighting(case_id):
    if request.method == 'POST':
        s = Sighting(
            case_id=case_id,
            reporter_id=session.get('user_id'),
            location_name=request.form.get('location_name'),
            latitude=request.form.get('latitude'),
            longitude=request.form.get('longitude'),
            description=request.form.get('description'),
            child_condition=request.form.get('child_condition'),
            adult_description=request.form.get('adult_description')
        )
        db.session.add(s)
        db.session.commit()
        flash("Sighting reported. High-priority alert sent to command.")
        return redirect(url_for('raksha_bp.view_case', case_id=case_id))
        
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('report_sighting.html', case_id=case_id, user=user)

@raksha_bp.route('/raksha/verify_sighting/<int:sighting_id>', methods=['POST'])
def verify_sighting(sighting_id):
    if 'user_id' not in session or session.get('user_role') not in ['ngo', 'organizer', 'admin']: 
        return redirect(url_for('login'))
        
    s = Sighting.query.get_or_404(sighting_id)
    s.is_verified = True
    db.session.commit()
    flash("Sighting verified. Updated on mission map.")
    return redirect(url_for('raksha_bp.view_case', case_id=s.case_id))

@raksha_bp.route('/organizer/download_aar')
def download_aar():
    if 'user_id' not in session or session.get('user_role') not in ['ngo', 'organizer', 'admin']: 
        return redirect(url_for('login'))
        
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Task ID', 'Title', 'Location', 'Status', 'Urgency', 'Skills', 'Created At'])
    
    for t in tasks:
        writer.writerow([t.id, t.title, t.location, t.status, t.urgency_score, t.required_skills, t.created_at])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=RAAKSHA_AAR_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"}
    )

@raksha_bp.route('/raksha/join/<int:case_id>', methods=['POST'])
def join_search(case_id):
    from models import SearchAssignment
    if 'user_id' not in session or session.get('user_role') != 'volunteer':
        return redirect(url_for('login'))
        
    case = MissingPersonCase.query.get_or_404(case_id)
    
    # Check if already joined
    existing = SearchAssignment.query.filter_by(case_id=case_id, volunteer_id=session['user_id']).first()
    if existing:
        flash("You have already joined this search mission.")
    else:
        assignment = SearchAssignment(
            case_id=case_id,
            volunteer_id=session['user_id'],
            status='Assigned'
        )
        db.session.add(assignment)
        db.session.commit()
        flash(f"You have joined the search for {case.name}. Please stay alert and report any sightings.")
        
    return redirect(url_for('volunteer_dashboard'))
