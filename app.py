from flask import Flask, render_template, session, redirect, url_for, request as flask_request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask import jsonify
from xuanxuan import xuanxuan_routes
from jc import jc_routes
from jamie import jamie_routes
from werkzeug.utils import secure_filename
import os
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)
app.register_blueprint(xuanxuan_routes)
app.register_blueprint(jc_routes)
app.register_blueprint(jamie_routes)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'junelson2002@gmail.com'
app.config['MAIL_PASSWORD'] = 'nkfmhtcnmnqhcvnc'

mail = Mail(app)


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
    owner = db.relationship('User', backref='listings')

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

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')


# =========================== DESIGN PATTERNS ===========================
class ListingNotifier:
    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def __getattr__(self, name):
        return getattr(self.wrapped, name)
    
    def notify(self, listing):
        for observer in self._observers:
            observer.update(listing)

class ListingFactory:
    @staticmethod
    def create_listing(type, data):
        return Listing(**data)

class ItemObserver:
    def update(self, listing):
        raise NotImplementedError

class AdminLogger(ItemObserver):
    def update(self, listing):
        print(f"[ADMIN LOG] Listing '{listing.title}' was posted by user ID {listing.owner_id}")

class EmailNotifier(ItemObserver):
    def update(self, listing):
        user = listing.owner  # assumes .owner relationship is loaded
        msg = Message(
            subject="🎉 Your item has been listed!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email]  # send to listing owner's email
        )
        msg.body = f"""
Hi {user.email},

Your item "{listing.title}" has just been listed on ShareBear!

Thanks for using our platform 😊
"""
        mail.send(msg)


class ListingDecorator:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def get_title(self):
        return self.wrapped.title

    def __getattr__(self, name):
        return getattr(self.wrapped, name)
    
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

class NotificationLogger(ItemObserver):
    def update(self, listing):
        user = listing.owner
        message = f"Your listing '{listing.title}' has been successfully posted."

        notification = Notification(user_id=user.id, message=message)
        db.session.add(notification)
        db.session.commit()
        

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
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
        return redirect(url_for('index'))
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
        return redirect(url_for('index'))

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
    return redirect(url_for('index'))


    
@app.route("/homepage",methods=['GET', 'POST'],endpoint='homepage')
def homepage():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    latest_listings = Listing.query.order_by(Listing.id.desc()).limit(30).all()
    decorated_listings = []
    for l in latest_listings:
        if l.status == 'featured':
            decorated_listings.append(FeaturedListing(l))
        elif l.status == 'urgent':
            decorated_listings.append(UrgentListing(l))
        elif l.status == 'verified':
            decorated_listings.append(VerifiedListing(l))
        else:
            decorated_listings.append(l)
    session.pop('listing_draft', None)
    return render_template('homepage.html',listings=decorated_listings)

@app.route('/sell_item', methods=['GET', 'POST'])
def sell_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('sell_item.html')


@app.route('/preview', methods=['POST'])
def preview_sellitem():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = flask_request.form
    file = flask_request.files.get('photos')  # just one file

    saved_filename = None

    if file and file.filename != '':
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ext = os.path.splitext(file.filename)[1]
        base_name = secure_filename(data.get('itemname', 'listing'))
        saved_filename = f"{base_name}_{timestamp}{ext}"

        file_path = os.path.join(UPLOAD_FOLDER, saved_filename)
        file.save(file_path)

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # or handle gracefully
    user = User.query.get(user_id)

    return render_template(
        'preview_sellitem.html',
        data=data,
        image=saved_filename,
        user=user
    )

@app.route('/saveListing', methods=['POST'])
def saveListing():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    form_data = {
        'title': flask_request.form.get('itemname'),
        'description': flask_request.form.get('description'),
        'condition': flask_request.form.get('condition'),
        'brand': flask_request.form.get('brand'),
        'dimensionSize': flask_request.form.get('size'),
        'color': flask_request.form.get('color'),
        'shippingOptions': flask_request.form.get('shipping'),
        'status': flask_request.form.get('status'),
        'owner_id': user_id,
        'image_filename': flask_request.form.get('image'),
        'category': flask_request.form.get('category'),
        'price': float(flask_request.form.get('itemprice')),
    }

    listing = ListingFactory.create_listing("default", form_data)
    db.session.add(listing)
    db.session.commit()

    # ✅ Notify observers
    notifier = ListingNotifier()
    notifier.register(AdminLogger())
    notifier.register(EmailNotifier())
    notifier.register(NotificationLogger())
    notifier.notify(listing)

    return redirect(url_for('itemsuccess'))

    
@app.route("/",endpoint='index')
def index():
    if 'user_id' in session:
        return redirect(url_for('homepage'))
    return render_template('index.html')

@app.route("/itemsuccess",endpoint='itemsuccess')
def itemsuccess():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('itemsuccess.html')

@app.route('/product/<int:product_id>',endpoint='product_page')
def product_page(product_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    product = Listing.query.get(product_id)
    if not product:
        return "Product not found", 404

    if product.status == 'featured':
        product = FeaturedListing(product)
    elif product.status == 'urgent':
        product = UrgentListing(product)
    elif product.status == 'verified':
        product = VerifiedListing(product)

    return render_template('productpage.html', product=product)
    
@app.route('/search', endpoint='search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    query = flask_request.args.get('q', '').strip()

    # If no query yet (user is typing), show suggestions
    if not query:
        suggestions = [listing.title for listing in Listing.query.limit(10).all()]
        return render_template('search_typing.html', suggestions=suggestions)

    # Perform search: title, category, or seller email
    listings = Listing.query.join(User).filter(
        (Listing.title.ilike(f"%{query}%")) |
        (Listing.category.ilike(f"%{query}%")) |
        (User.email.ilike(f"%{query}%"))
    ).all()

    if not listings:
        related_products = Listing.query.order_by(Listing.id.desc()).limit(8).all()
        return render_template('search_noresults.html',
                               query=query,
                               related_products=related_products)

    return render_template('search_results.html',
                           query=query,
                           products=listings,
                           total_results=len(listings))


categories = [
    {"name": "Women's Closet", "image": "women.png"},
    {"name": "Men's Wardrobe", "image": "men.png"},
    {"name": "Books & Magazines", "image": "books.png"},
    {"name": "Gadgets & Gear", "image": "gadgets.png"},
    {"name": "Musical Instruments", "image": "instrument.png"},
    {"name": "Beauty & Wellness", "image": "beauty.png"},
    {"name": "Accessories", "image": "gadgets.png"},
]


@app.route('/categories',endpoint='categories_page')
def categories_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('categories.html', categories=categories)

@app.route('/category/<category_name>',endpoint='category_products')
def category_products(category_name):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    # Proper query using filter_by
    category_items = Listing.query.filter_by(category=category_name).all()

    # Optionally decorate listings (if using decorator pattern)
    decorated_items = []
    for l in category_items:
        if l.status == 'featured':
            decorated_items.append(FeaturedListing(l))
        elif l.status == 'urgent':
            decorated_items.append(UrgentListing(l))
        elif l.status == 'verified':
            decorated_items.append(VerifiedListing(l))
        else:
            decorated_items.append(l)

    return render_template(
        'category_products.html',
        category_name=category_name,
        products=decorated_items,
        categories=categories  # for sidebar/category menu
    )

@app.route('/notification',endpoint='notification')
def notification():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user_id = session.get('user_id')

    # Fetch notifications from DB
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False) \
                                  .order_by(Notification.created_at.desc()) \
                                  .all()
    return render_template('notification.html', notifications=notifications)

@app.route('/notification/<int:index>', endpoint='notification_detail')
def notification_detail(index):
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # Fetch the notification
    note = Notification.query.get(index)

    # ✅ Only allow if it exists and belongs to current user
    if not note or note.user_id != user_id:
        return "Notification not found or access denied", 404

    # Mark as read
    if not note.is_read:
        note.is_read = True
        db.session.commit()

    return render_template('notification_detail.html', note=note)

@app.route('/mark_all_read', methods=['POST'],endpoint='mark_all_read')
def mark_all_read():
    user_id=session.get('user_id')
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False) \
                                  .order_by(Notification.created_at.desc()) \
                                  .all()
    for note in notifications:
        note.is_read = True
        db.session.commit()
    
    return redirect(flask_request.referrer)

@app.route('/myprofile',endpoint='myprofile')
def myprofile():
    user_id=session.get('user_id')
    user = User.query.get(user_id)
    
    return render_template('myprofile.html', user=user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
