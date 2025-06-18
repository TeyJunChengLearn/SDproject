from flask import Blueprint,render_template,session, redirect, url_for, request as flask_request,jsonify;

xuanxuan_routes = Blueprint('xuanxuan_routes', __name__)

@xuanxuan_routes.route('/charity', endpoint='charity')
def charity():
    dummy_charities = [
        {
            "name": "Yayasan Harapan Murni",
            "address": "12, Jalan Damai, 43000 Kajang, Selangor",
            "donators": 532,
            "image": "static/charity.png"
        },
        {
            "name": "Kasih Abadi Foundation",
            "address": "Lot 45, Taman Sinaran, 11800 Gelugor, Pulau Pinang",
            "donators": 289,
            "image": "static/charity.png"
        },
        {
            "name": "HopeBridge Relief",
            "address": "29A, Jalan Rahmat, 81000 Kulai, Johor",
            "donators": 745,
            "image": "static/charity.png"
        }
    ]
    return render_template('charity.html', charities=dummy_charities)

@xuanxuan_routes.route('/charity/donate')
def charity_donate():
    return render_template('charity_donate.html')

@xuanxuan_routes.route('/charity/confirmation')
def charity_confirmation():
    return render_template('charity_confirmation.html')
