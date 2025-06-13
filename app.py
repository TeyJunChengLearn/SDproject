from flask import Flask, render_template, session, redirect, url_for, request as flask_request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask import jsonify
from xuanxuan import xuanxuan_routes
from jc import jc_routes
from jamie import jamie_routes
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)
app.register_blueprint(xuanxuan_routes)
app.register_blueprint(jc_routes)
app.register_blueprint(jamie_routes)
# =========================== MODELS ===========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    avatar_filename = db.Column(db.String(255), nullable=True)
    requests = db.relationship('Request', backref='requester', lazy=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    transactions = db.relationship('Transaction', foreign_keys='Transaction.buyer_id', backref='buyer', lazy=True)

class Admin(User):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

class Charity(User):
    __tablename__ = 'charity'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(db.Text, nullable=True)
    brand = db.Column(db.Text, nullable=True)
    dimensionSize = db.Column(db.Text, nullable=True)
    color = db.Column(db.Text, nullable=True)
    shippingOptions = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    offered_listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'))  # listing being given
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    decision_time = db.Column(db.DateTime)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    strategy = None

    __mapper_args__ = {
        'polymorphic_identity': 'request',
        'polymorphic_on': type
    }

    def approve(self):
        if self.strategy:
            self.strategy.approve(self)

    def reject(self):
        if self.strategy:
            self.strategy.reject(self)

    def set_strategy(self, strategy):
        self.strategy = strategy

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')  # open, in_progress, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='support_tickets')



class BorrowRequest(Request):
    __tablename__ = 'borrow_request'
    id = db.Column(db.Integer, db.ForeignKey('request.id'), primary_key=True)
    borrow_start = db.Column(db.Date)
    borrow_end = db.Column(db.Date)
    __mapper_args__ = {
        'polymorphic_identity': 'borrow_request'
    }

class TradeRequest(Request):
    __tablename__ = 'trade_request'
    id = db.Column(db.Integer, db.ForeignKey('request.id'), primary_key=True)
    offered_item_id = db.Column(db.Integer, db.ForeignKey('listing.id'))
    __mapper_args__ = {
        'polymorphic_identity': 'trade_request'
    }

class DonationRequest(Request):
    __tablename__ = 'donation_request'
    id = db.Column(db.Integer, db.ForeignKey('request.id'), primary_key=True)
    reason = db.Column(db.String(255))
    __mapper_args__ = {
        'polymorphic_identity': 'donation_request'
    }

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    generated_by = db.Column(db.Integer, db.ForeignKey('admin.id'))
    data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='cart')
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)

    listing = db.relationship('Listing')

# =========================== DESIGN PATTERNS ===========================

class ListingFactory:
    @staticmethod
    def create_listing(type, data):
        return Listing(**data)

class ItemObserver:
    def update(self, listing):
        raise NotImplementedError

class ListingDecorator:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def get_title(self):
        return self.wrapped.title

    def get_description(self):
        return self.wrapped.description

class FeaturedListing(ListingDecorator):
    def get_title(self):
        return "[FEATURED] " + super().get_title()

class UrgentListing(ListingDecorator):
    def get_title(self):
        return "[URGENT] " + super().get_title()

class VerifiedListing(ListingDecorator):
    def get_title(self):
        return "[VERIFIED] " + super().get_title()

class RequestStrategy:
    def approve(self, request):
        raise NotImplementedError

    def reject(self, request):
        raise NotImplementedError

class BorrowStrategy(RequestStrategy):
    def approve(self, request):
        request.status = "approved"

    def reject(self, request):
        request.status = "rejected"

class TradeStrategy(RequestStrategy):
    def approve(self, request):
        request.status = "approved"

    def reject(self, request):
        request.status = "rejected"

class ReportGenerator:
    _instance = None

    @staticmethod
    def get_instance():
        if ReportGenerator._instance is None:
            ReportGenerator._instance = ReportGenerator()
        return ReportGenerator._instance

    def generate_report(self, admin_id):
        return Report(generated_by=admin_id, data="System Report", created_at=datetime.utcnow())

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# =========================== ROUTES ===========================

@app.route("/createacc",methods=['GET','POST'],endpoint='createacc')
def createacc():
    if 'user_id' in session:
        return redirect(url_for('homepage'))

    if flask_request.method == 'POST':
        email = flask_request.form.get("email")
        password = flask_request.form.get("password")
        phone = flask_request.form.get("phone")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "error")
            return redirect(url_for('createacc'))

        # ✅ FIXED THIS LINE
        avatar_file = flask_request.files.get('avatar')
        avatar_filename = None

        if avatar_file and avatar_file.filename != '':
            ext = avatar_file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = secure_filename(f"user_{timestamp}.{ext}")
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # ✅ make sure directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            avatar_file.save(save_path)
            avatar_filename = filename
        else:
            flash("No image selected or image invalid.", "error")
            return redirect(url_for('createacc'))

        new_user = User(
            email=email,
            password=password,
            phone_number=phone,
            status='active',
            avatar_filename=avatar_filename
        )
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['user_email'] = new_user.email

        return redirect(url_for('homepage'))

    return render_template('createaccount.html')

@app.route('/myaccount',endpoint='myaccount')
def myaccount():
    if 'user_id' not in session:
        return redirect(url_for('xuanxuan_routes.index'))
    else:
        user=User.query.get(session.get('user_id'))
        return render_template('myaccount.html',user=user)

@app.route("/login", methods=['GET', 'POST'], endpoint='login')
def login():
    if 'user_id' in session:
        return redirect(url_for('homepage'))

    if flask_request.method == "POST":
        user = User.query.filter_by(email=flask_request.form.get('email')).first()

        if not user:
            flash("Email not found. Please register first.", "error")
            return redirect(url_for('login'))

        session['email'] = user.email

        return redirect(url_for('password'))

    return render_template('login.html')  # This will handle GET correctly

@app.route("/insertpassword", methods=['GET', 'POST'], endpoint='password')
def password():
    # Redirect if user is NOT logged in
    if 'email' not in session:
        return redirect(url_for('xuanxuan_routes.index'))

    # Optionally skip if password is already set or user is fully logged in
    if 'user_id' in session:
        return redirect(url_for('homepage'))

    email = session.get('email')

    # If it's POST, you can handle password verification here
    if flask_request.method == 'POST':
        password_input = flask_request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or user.password != password_input:
            flash("Incorrect password.", "error")
            return redirect(url_for('password'))

        # Log in the user fully
        session['user_id'] = user.id
        return redirect(url_for('homepage'))

    return render_template('insertpassword.html', email=email)


@app.route("/logout",endpoint='logout')
def logout():
    session.clear()
    return redirect(url_for('xuanxuan_routes.index'))


    
@app.route("/homepage",methods=['GET', 'POST'],endpoint='homepage')
def homepage():
    if 'user_id' not in session:
        return redirect(url_for('xuanxuan_routes.index'))
    session.pop('listing_draft', None)
    return render_template('homepage.html')

@app.route('/sell_item', methods=['GET', 'POST'])
def sell_item():
    return render_template('sell_item.html')


@app.route('/preview', methods=['POST'])
def preview_sellitem():
    data = flask_request.form
    files = flask_request.files.getlist('photos')
    # You can process/store images here
    return render_template('preview_sellitem.html', data=data, images=files)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
