from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database.models import User, Subject, Syllabus, StudyPlan, db
from functools import wraps
import threading

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.home'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def index():
    from database.models import Syllabus
    total_users   = User.query.count()
    total_syllabi = Syllabus.query.count()
    failed_syllabi = Syllabus.query.filter_by(processing_status='failed').count()
    recent_users  = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
        total_users=total_users,
        total_syllabi=total_syllabi,
        failed_syllabi=failed_syllabi,
        recent_users=recent_users,
    )


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    from database.models import Syllabus
    users = User.query.order_by(User.created_at.desc()).all()
    failed_syllabi = Syllabus.query.filter_by(processing_status='failed').count()
    return render_template('admin/users.html', users=users, failed_syllabi=failed_syllabi)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot suspend your own account.', 'error')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activated' if user.is_active else 'suspended'
        flash(f'User {user.email} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f'User {email} has been permanently deleted.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/syllabi')

@login_required
@admin_required
def syllabi():
    syllabi = Syllabus.query.order_by(Syllabus.uploaded_at.desc()).limit(50).all()
    failed_syllabi = Syllabus.query.filter_by(processing_status='failed').count()
    return render_template('admin/syllabi.html', syllabi=syllabi, failed_syllabi=failed_syllabi)


@admin_bp.route('/failed-parses')
@login_required
@admin_required
def failed_parses():
    failed = Syllabus.query.filter_by(
        processing_status='failed'
    ).order_by(Syllabus.uploaded_at.desc()).all()
    return render_template('admin/failed_parses.html', failed=failed)


@admin_bp.route('/syllabi/<int:syllabus_id>/reprocess', methods=['POST'])
@login_required
@admin_required
def reprocess(syllabus_id):
    from flask import current_app
    from routes.upload import process_syllabus_background   # ← fixed import

    syllabus = Syllabus.query.get_or_404(syllabus_id)
    syllabus.processing_status = 'processing'
    syllabus.error_message     = None
    db.session.commit()

    app    = current_app._get_current_object()
    thread = threading.Thread(
        target=process_syllabus_background,
        args=(app, syllabus.id)
    )
    thread.daemon = True
    thread.start()

    flash(f'Reprocessing started for "{syllabus.original_filename}".', 'success')
    return redirect(url_for('admin.failed_parses'))