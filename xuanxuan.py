from flask import Blueprint,render_template,session, redirect, url_for, request as flask_request,jsonify;

xuanxuan_routes = Blueprint('xuanxuan_routes', __name__)

'''
@xuanxuan_routes.route('/charity', endpoint='charity')
def charity():
    charities=charity.query.all()
    return render_template('charity.html', charities=charities)

@xuanxuan_routes.route('/charity/donate/<charity_id>')
def charity_donate(charity_id):
    # Dummy user products
    user_products = [
        {
            'id': 1,
            'name': 'Zara Classic White Shirt - White',
            'image': 'shirt.png'
        },
        {
            'id': 2,
            'name': 'Zara Classic White Shirt - White',
            'image': 'marita.png'
        }
    ]

    # Empty list to test no products case
    # user_products = []

    return render_template('charity_donate.html', charity_id=charity_id, user_products=user_products)

@xuanxuan_routes.route('/charity/confirmation')
def charity_confirmation():
    return render_template('charity_confirmation.html')
'''