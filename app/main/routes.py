from flask import render_template, redirect

from app.main import bp


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
