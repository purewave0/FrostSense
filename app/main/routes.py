from flask import render_template, redirect, abort
from flask_login import current_user

from app.main import bp
from app.api.report import get_report_file


@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect('/readings')

    return render_template('login.html')


@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect('/login')

    return redirect('/readings')

# TODO: login_required for the routes below

@bp.route('/readings')
def readings():
    return render_template('main/sections/readings.html')

@bp.route('/history')
def history():
    return render_template('main/sections/history.html')

@bp.route('/sensors')
def sensors():
    return render_template('main/sections/sensors.html')

@bp.route('/reports')
def reports():
    return render_template('main/sections/reports.html')

@bp.route('/reports/<code>')
def get_report(code):
    try:
        report_html = get_report_file(code)
    except IOError:
        return abort(404)

    return report_html

@bp.route('/verify-reports')
def verify_reports():
    return render_template('main/sections/verify-reports.html')
