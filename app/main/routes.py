from flask import render_template, redirect

from app.main import bp


@bp.route('/')
def index():
    return redirect('/readings')

@bp.route('/readings')
def readings():
    return render_template('main/sections/readings.html')

@bp.route('/sensors')
def sensors():
    return render_template('main/sections/sensors.html')
