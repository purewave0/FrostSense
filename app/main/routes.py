from flask import render_template, redirect, abort, url_for
from flask_login import current_user, login_required, logout_user

from app.main import bp
from app.api.report import get_report_file
from app.models.users import User
from app.util import permission_required


@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect('/')

    return render_template('login.html')


@bp.route('/')
@login_required
def index():
    return redirect('/' + current_user.homepage)


@bp.route('/readings')
@login_required
def readings():
    return render_template('main/sections/readings.html')

@bp.route('/history')
@login_required
def history():
    return render_template('main/sections/history.html')

@bp.route('/sensors')
@login_required
def sensors():
    return render_template('main/sections/sensors.html')

@bp.route('/reports')
@login_required
@permission_required(User.Permission.MANAGE_REPORTS)
def reports():
    return render_template('main/sections/reports.html')

@bp.route('/reports/<code>')
@login_required
@permission_required(User.Permission.MANAGE_REPORTS)
def get_report(code):
    try:
        report_html = get_report_file(code)
    except IOError:
        return abort(404)

    return report_html

@bp.route('/verify-reports')
@login_required
@permission_required(User.Permission.MANAGE_REPORTS)
def verify_reports():
    return render_template('main/sections/verify-reports.html')

@bp.route('/preferences')
@login_required
def own_preferences():
    return render_template('main/preferences.html')

@bp.route('/logout')
@login_required
def main_logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/users')
@login_required
@permission_required(User.Permission.MANAGE_USERS)
def users():
    return render_template('main/sections/users.html')

@bp.route('/system-settings')
@login_required
@permission_required(User.Permission.MANAGE_SYSTEM_SETTINGS)
def system_settings():
    return render_template('main/system-settings.html')

@bp.route('/create-password')
@login_required
def create_own_password():
    if not current_user.is_password_temporary:
        # no use coming here if you already have a permanent password
        return redirect(url_for('main.index'))

    return render_template('main/create-password.html')
