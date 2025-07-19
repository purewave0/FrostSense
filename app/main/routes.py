from flask import render_template, redirect, abort

from app.main import bp
from app.api.report import get_report_file


@bp.route('/')
def index():
    return redirect('/readings')

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

@bp.route('/reports/<token>')
def get_report(token):
    try:
        report_html = get_report_file(token)
    except IOError:
        return abort(404)

    return report_html
