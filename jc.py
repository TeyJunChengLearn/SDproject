from flask import Blueprint,render_template,session, redirect, url_for, request as flask_request;

jc_routes = Blueprint('jc_routes', __name__)