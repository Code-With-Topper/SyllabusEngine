from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json




class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='student')  # 'student' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_calendar_token = db.Column(db.Text, nullable=True)
    email_preferences = db.Column(db.Text, default='{"weekly_preview": true, "monday_alert": true, "exam_warning": true}')

    subjects = db.relationship('Subject', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_student(self):
        return self.role == 'student'

    def get_email_prefs(self):
        return json.loads(self.email_preferences)


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    color = db.Column(db.String(7), default='#6366f1')
    semester_length = db.Column(db.Integer, default=15)
    start_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    syllabi = db.relationship('Syllabus', backref='subject', lazy=True, cascade='all, delete-orphan')
    study_plans = db.relationship('StudyPlan', backref='subject', lazy=True, cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='subject', lazy=True, cascade='all, delete-orphan')
    calendar_events = db.relationship('CalendarEvent', backref='subject', lazy=True, cascade='all, delete-orphan')
    conversations = db.relationship('AIConversation', backref='subject', lazy=True, cascade='all, delete-orphan')

    @property
    def latest_plan(self):
        return StudyPlan.query.filter_by(subject_id=self.id).order_by(StudyPlan.generated_at.desc()).first()

    @property
    def completion_pct(self):
        plan = self.latest_plan
        if not plan:
            return 0
        total = Week.query.filter_by(study_plan_id=plan.id).count()
        if total == 0:
            return 0
        completed = Progress.query.filter_by(subject_id=self.id, is_completed=True).count()
        return min(100, int((completed / (total * 3)) * 100))


class Syllabus(db.Model):
    __tablename__ = 'syllabi'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(200))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(50), default='queued')  # queued, processing, completed, failed
    ocr_used = db.Column(db.Boolean, default=False)
    confidence_score = db.Column(db.Float, default=0.0)
    extracted_text = db.Column(db.Text, nullable=True)
    raw_ai_output = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)


class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    syllabus_id = db.Column(db.Integer, db.ForeignKey('syllabi.id'), nullable=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    course_title = db.Column(db.String(200))
    instructor = db.Column(db.String(200))
    json_raw = db.Column(db.Text)

    weeks = db.relationship('Week', backref='study_plan', lazy=True, cascade='all, delete-orphan', order_by='Week.week_number')
    exams = db.relationship('Exam', backref='study_plan', lazy=True, cascade='all, delete-orphan')

    def get_json(self):
        return json.loads(self.json_raw) if self.json_raw else {}


class Week(db.Model):
    __tablename__ = 'weeks'
    id = db.Column(db.Integer, primary_key=True)
    study_plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    date_start = db.Column(db.Date, nullable=True)
    date_end = db.Column(db.Date, nullable=True)
    topics = db.Column(db.Text, default='[]')       # JSON array
    key_concepts = db.Column(db.Text, default='[]') # JSON array
    difficulty = db.Column(db.String(20), default='medium')
    recommended_hours = db.Column(db.Integer, default=6)
    readings = db.Column(db.Text, default='[]')     # JSON array
    revision_tasks = db.Column(db.Text, default='[]')
    study_advice = db.Column(db.Text)
    is_exam_week = db.Column(db.Boolean, default=False)
    completion_pct = db.Column(db.Integer, default=0)

    assignments = db.relationship('Assignment', backref='week', lazy=True)

    def get_topics(self):
        return json.loads(self.topics) if self.topics else []

    def get_concepts(self):
        return json.loads(self.key_concepts) if self.key_concepts else []

    def get_readings(self):
        return json.loads(self.readings) if self.readings else []

    def get_revision_tasks(self):
        return json.loads(self.revision_tasks) if self.revision_tasks else []


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=True)
    estimated_hours = db.Column(db.Float, default=2.0)
    preparation_steps = db.Column(db.Text, default='[]')
    is_completed = db.Column(db.Boolean, default=False)
    confidence = db.Column(db.String(10), default='high')  # high, medium, low
    google_event_id = db.Column(db.String(200))

    def get_steps(self):
        return json.loads(self.preparation_steps) if self.preparation_steps else []


class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    study_plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    exam_date = db.Column(db.Date, nullable=True)
    coverage_weeks = db.Column(db.Text, default='[]')
    preparation_plan = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    confidence = db.Column(db.String(10), default='high')
    google_event_id = db.Column(db.String(200))

    def get_coverage(self):
        return json.loads(self.coverage_weeks) if self.coverage_weeks else []


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    event_type = db.Column(db.String(30))  # study, deadline, exam, revision
    title = db.Column(db.String(300))
    description = db.Column(db.Text)
    event_date = db.Column(db.Date)
    duration_minutes = db.Column(db.Integer, default=60)
    google_event_id = db.Column(db.String(200))
    synced_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=True)
    item_type = db.Column(db.String(30))  # topic, assignment, revision
    item_key = db.Column(db.String(200))
    is_completed = db.Column(db.Boolean, default=False)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)


class AIConversation(db.Model):
    __tablename__ = 'ai_conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    role = db.Column(db.String(10))  # user, assistant
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OAuthToken(db.Model):
    __tablename__ = 'oauth_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String(30), default='google')
    token_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

