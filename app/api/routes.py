from flask import jsonify

from app.api import bp


@bp.route('/test')
def api_test():
    print('oi')
    return jsonify('test')
