from flask import Blueprint,render_template,session, redirect, url_for, request as flask_request;

jamie_routes = Blueprint('jamie_routes', __name__)