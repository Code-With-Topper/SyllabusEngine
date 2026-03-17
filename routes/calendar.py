from flask import Blueprint, render_template
from flask_login import login_required, current_user
from database.models import Subject, Assignment, Exam
import json

# This is the authoritative calendar blueprint.
# app.py imports: from routes.calendar import calendar_bp
# routes/assistant.py must NOT define its own calendar_bp — it imports this one.
calendar_bp = Blueprint('calendar', __name__)


@calendar_bp.route('/subjects/<int:subject_id>/calendar')
@login_required
def view(subject_id):
    subject     = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    assignments = Assignment.query.filter_by(subject_id=subject_id).all()
    exams       = []
    plan        = subject.latest_plan

    if plan:
        exams = Exam.query.filter_by(study_plan_id=plan.id).all()

    events = []

    for a in assignments:
        if a.due_date:
            events.append({
                'title': f'📋 {a.title}',
                'start': a.due_date.isoformat(),
                'color': '#f97316',
                'type':  'assignment',
            })

    for e in exams:
        if e.exam_date:
            events.append({
                'title': f'📝 {e.name}',
                'start': e.exam_date.isoformat(),
                'color': '#ef4444',
                'type':  'exam',
            })

    return render_template('dashboard/calendar.html',
        subject=subject,
        events=json.dumps(events),
    )