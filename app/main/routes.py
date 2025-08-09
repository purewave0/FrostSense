from flask import render_template, redirect, abort
from flask_login import current_user, login_required

from app.main import bp
from app.api.report import get_report_file


@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect('/readings')

    return render_template('login.html')


@bp.route('/')
@login_required
def index():
    return redirect('/readings')


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
def reports():
    return render_template('main/sections/reports.html')

@bp.route('/reports/<code>')
@login_required
def get_report(code):
    try:
        report_html = get_report_file(code)
    except IOError:
        return abort(404)

    return report_html

@bp.route('/verify-reports')
@login_required
def verify_reports():
    return render_template('main/sections/verify-reports.html')
