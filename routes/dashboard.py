from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database.models import Subject, Assignment, Week, db
from datetime import date, datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    subjects = Subject.query.filter_by(user_id=current_user.id, is_active=True).all()
    today = date.today()

    upcoming_deadlines = (
        Assignment.query
        .join(Subject)
        .filter(
            Subject.user_id == current_user.id,
            Assignment.due_date >= today,
            Assignment.due_date <= today + timedelta(days=14),
            Assignment.is_completed == False
        )
        .order_by(Assignment.due_date)
        .limit(8)
        .all()
    )

    subject_data = []
    for s in subjects:
        plan = s.latest_plan
        current_week = None
        if plan and s.start_date:
            weeks_elapsed = (today - s.start_date).days // 7 + 1
            current_week = Week.query.filter_by(
                study_plan_id=plan.id,
                week_number=min(max(weeks_elapsed, 1), s.semester_length)
            ).first()
        subject_data.append({
            'subject':      s,
            'plan':         plan,
            'current_week': current_week,
            'completion':   s.completion_pct,
        })

    return render_template('dashboard/home.html',
        subject_data=subject_data,
        upcoming_deadlines=upcoming_deadlines,
        today=today,
        now=datetime.now(),          # ← needed by template for greeting
    )


@dashboard_bp.route('/api/progress/toggle', methods=['POST'])
@login_required
def toggle_progress():
    data      = request.get_json()
    item_type = data.get('type')
    item_id   = data.get('id')

    if item_type == 'assignment':
        from database.models import Assignment
        assignment = Assignment.query.get(item_id)
        if assignment and assignment.subject.user_id == current_user.id:
            assignment.is_completed = not assignment.is_completed
            db.session.commit()
            return jsonify({'success': True, 'completed': assignment.is_completed})

    return jsonify({'success': False})