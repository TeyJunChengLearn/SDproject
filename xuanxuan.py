from flask import Blueprint,render_template,session, redirect, url_for, request as flask_request,jsonify;

xuanxuan_routes = Blueprint('xuanxuan_routes', __name__)