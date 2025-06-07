from flask import Flask, render_template, session, redirect, url_for, request as flask_request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)

# =========================== MODELS ===========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    requests = db.relationship('Request', backref='requester', lazy=True)
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
    status = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100), nullable=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
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


class PurchaseRequest(Request):
    __tablename__ = 'purchase_request'
    id = db.Column(db.Integer, db.ForeignKey('request.id'), primary_key=True)
    proposed_price = db.Column(db.Float)
    __mapper_args__ = {
        'polymorphic_identity': 'purchase_request'
    }

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

class PurchaseStrategy(RequestStrategy):
    def approve(self, request):
        request.status = "approved"

    def reject(self, request):
        request.status = "rejected"

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

# =========================== ROUTES ===========================

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/createacc")
def createacc():
    return render_template('createaccount.html')

@app.route("/insertpassword")
def password():
    return render_template('insertpassword.html')

@app.route("/homepage")
def homepage():
    return render_template('homepage.html')

dummy_products = {
    1: {
        "name": "Blouse Besaty White Blue Beau",
        "original_price": 48,
        "discounted_price": None,
        "description": "Beautiful H&M blouse with blue floral pattern.",
        "image_path": "beau.png",
        "seller_name": "H&M",
        "location_image": "map1.png"
    },
    2: {
        "name": "Zara Classic White Shirt - White - M",
        "original_price": 58,
        "discounted_price": 28,
        "description": "Zara's clean-cut white shirt for modern style.",
        "image_path": "shirt.png",
        "seller_name": "H&M",
        "location_image": "map2.png"
    },
    3: {
        "name": "Zara Classic Man Black Shirt",
        "original_price": 60,
        "discounted_price": 28,
        "description": "Elegant black shirt by Zara for men.",
        "image_path": "blackshirt.png",
        "seller_name": "Vrinda",
        "location_image": "map3.png"
    },
    4: {
        "name": "Sleeveless Rock Black Marita",
        "original_price": 55,
        "discounted_price": None,
        "description": "Stylish sleeveless dress perfect for events.",
        "image_path": "marita.png",
        "seller_name": "Barbara",
        "location_image": "map4.png"
    },
    5: {
        "name": "Blouse Besaty White Blue Beau",
        "original_price": 48,
        "discounted_price": None,
        "description": "Same stylish blouse, another listing.",
        "image_path": "beau.png",
        "seller_name": "H&M",
        "location_image": "map1.png"
    },
    6: {
        "name": "Zara Classic White Shirt - White - M",
        "original_price": 58,
        "discounted_price": 28,
        "description": "Another listing for Zara classic white shirt.",
        "image_path": "shirt.png",
        "seller_name": "H&M",
        "location_image": "map2.png"
    }
}

# Search suggestions
search_suggestions = [
    "Zara White Shirt",
    "Zara Black Blazer for Women", 
    "Zara Men's Casual Jackets",
    "Zara Kids Clothing",
    "Zara Leather Handbags",
    "Zara Summer Collection",
    "Zara Office Wear"
]

# Related products for no results page
related_products = [
    {"name": "Buy Luna Puff Beige Dress", "seller_name": "Barbara", "price": 28, "is_new": True},
    {"name": "Zara Classic White Shirt - White - M", "seller_name": "H&M", "price": 28, "is_new": True},
    {"name": "Basic White Tee", "seller_name": "Uniqlo", "price": 25, "is_new": False},
    {"name": "Black Cotton Shirt", "seller_name": "Zara", "price": 35, "is_new": False, "is_liked": True}
]

categories = [
    {"name": "Women's Closet", "image": "women.png"},
    {"name": "Men's Wardrobe", "image": "men.png"},
    {"name": "Books & Magazines", "image": "books.png"},
    {"name": "Gadgets & Gear", "image": "gadgets.png"},
    {"name": "Musical Instruments", "image": "instrument.png"},
    {"name": "Beauty & Wellness", "image": "beauty.png"},
    {"name": "Accessories", "image": "gadgets.png"},
]

products = {
    "Women's Closet": [
        {"brand": "H&M", "name": "Blouse Besaty White", "original_price": "Rm35", "discounted_price": "Rm28", "image": "beau.png"},
        {"brand": "Barbara", "name": "Sleeveless Rock", "original_price": "Rm28", "image": "women.png"}
    ],
    "Men's Wardrobe": [
        {"brand": "Zara", "name": "Zara Classic Black Shirt", "original_price": "Rm38", "discounted_price": "Rm28", "image": "men.png"},
        {"brand": "H&M", "name": "Zara Classic White Shirt", "original_price": "Rm28", "image": "shirt.png"}
    ],
    "Books & Magazines": [
        {"brand": "Reader's Digest", "name": "Health & Wellness 2023", "original_price": "Rm20", "discounted_price": "Rm15", "image": "books.png"},
        {"brand": "Penguin", "name": "Classic Novels Set", "original_price": "Rm45", "image": "books.png"}
    ],
    "Gadgets & Gear": [
        {"brand": "Samsung", "name": "Wireless Earbuds", "original_price": "Rm150", "discounted_price": "Rm120", "image": "gadgets.png"},
        {"brand": "Logitech", "name": "Bluetooth Mouse", "original_price": "Rm60", "image": "gadgets.png"}
    ],
    "Musical Instruments": [
        {"brand": "Yamaha", "name": "Acoustic Guitar", "original_price": "Rm300", "discounted_price": "Rm280", "image": "instrument.png"},
        {"brand": "Casio", "name": "Keyboard Piano", "original_price": "Rm350", "image": "instrument.png"}
    ],
    "Beauty & Wellness": [
        {"brand": "The Body Shop", "name": "Aloe Vera Skincare Set", "original_price": "Rm88", "image": "beauty.png"},
        {"brand": "L'Oreal", "name": "Hair Color Kit", "original_price": "Rm45", "discounted_price": "Rm38", "image": "beauty.png"}
    ],
    "Accessories": [
        {"brand": "Zara", "name": "Leather Handbag", "original_price": "Rm120", "discounted_price": "Rm99", "image": "marita.png"},
        {"brand": "H&M", "name": "Gold Earrings", "original_price": "Rm28", "image": "shirt.png"},
        {"brand": "Zara", "name": "Leather Handbag", "original_price": "Rm120", "discounted_price": "Rm99", "image": "marita.png"}
    ]
}

@app.route('/search')
def search():
    query = flask_request.args.get('q', '').strip()
    
    related_products = []
    for pid, pdata in dummy_products.items():
        product_copy = pdata.copy()
        product_copy['id'] = pid
        related_products.append(product_copy)

    if not query:
        # Show typing state with suggestions
        search_suggestions = list({p['name'] for p in dummy_products.values()})
        return render_template('search_typing.html', suggestions=search_suggestions)
    
    # Filter products based on query
    filtered_products = []
    for product_id, product in dummy_products.items():
        if (query.lower() in product['name'].lower() or 
            query.lower() in product['seller_name'].lower()):
            product_copy = product.copy()
            product_copy['id'] = product_id
            filtered_products.append(product_copy)
    
    if not filtered_products:
        # Show no results state
        return render_template('search_noresults.html', 
                             query=query, 
                             related_products=related_products)
    
    # Show results state
    most_viewed = filtered_products[:4]  # First 4 as most viewed
    other_results = filtered_products[4:]  # Rest as other results
    
    return render_template('search_results.html', 
                         query=query,
                         most_viewed=most_viewed,
                         other_results=other_results,
                         total_results=len(filtered_products))

@app.route('/api/like/<int:product_id>', methods=['POST'])
def toggle_like(product_id):
    # In a real app, you'd save this to a database
    # For now, just return success
    return jsonify({'success': True, 'liked': True})

@app.route("/sellitem/<int:step>")
def sellitem(step):
    if step == 1:
        return render_template("sellitem.html")
    else:
        return render_template(f"sellitem{step}.html")

@app.route("/itemsuccess")
def itemsuccess():
    return render_template('itemsuccess.html')

@app.route('/product/<int:product_id>')
def product_page(product_id):
    product = dummy_products.get(product_id)
    if not product:
        return "Product not found", 404

    product_copy = product.copy()
    product_copy['id'] = product_id  # add id here

    if product_copy['discounted_price'] is None or product_copy['discounted_price'] >= product_copy['original_price']:
        product_copy['discounted_price'] = product_copy['original_price']

    return render_template('productpage.html', product=product_copy)

@app.route('/categories')
def categories_page():
    return render_template('categories.html', categories=categories)

@app.route('/category/<category_name>')
def category_products(category_name):
    category_items = products.get(category_name, [])
    return render_template('category_products.html', category_name=category_name, products=category_items, categories=categories)

@app.route('/myaccount')
def myaccount():
    return render_template('myaccount.html')

@app.route('/myprofile')
def myprofile():
    # Dummy user data
    user = {
        'name': 'Lucia Smith',
        'email': 'luciasmith@example.com',
        'phone': '+1 234 567 890',
        'address': '123-45 Gangnam-daero, Gangnam-gu, Seoul, South Korea, 06050'
    }
    return render_template('myprofile.html', user=user)

notifications = [
    {
        'title': 'How do you feel about your recent order?',
        'desc': "You've successfully completed your order for the new Converse [Model Name]. We'd love to hear your feedback!",
        'link': 'Submit Your Review',
        'time': '2 minutes ago',
        'read': False,
        'color': 'black'
    },
    {
        'title': 'Great News: Your Order Payment Was Successful!',
        'desc': "Your payment has been processed successfully! Check out the latest Converse collection before they're gone.",
        'link': None,
        'time': 'Just now',
        'read': False,
        'color': 'blue'
    },
    {
        'title': 'Great News: Your Order Has Been Shipped!',
        'desc': "Your order is on its way! Check out the latest Converse styles while you wait.",
        'link': None,
        'time': 'Just now',
        'read': False,
        'color': 'blue'
    }
]

@app.route('/notification')
def notification():
    return render_template('notification.html', notifications=notifications)

@app.route('/mark_all_read', methods=['POST'])
def mark_all_read():
    for note in notifications:
        note['read'] = True
        note['color'] = 'black'
    return jsonify({'status': 'success'})

@app.route('/notification/<int:index>')
def notification_detail(index):
    if 0 <= index < len(notifications):
        notifications[index]['read'] = True
        notifications[index]['color'] = 'black'
        return render_template('notification_detail.html', note=notifications[index])
    return "Notification not found", 404

@app.route('/myorders')
def my_orders():
    sample_orders = [
        {'id': '879234', 'name': '1x Floral Summer Dress', 'status': 'Completed', 'total': '120.00', 'date': 'February 20, 2024', 'image': 'marita.png'},
        {'id': '879234', 'name': '1x Floral Summer Dress', 'status': 'In Process', 'total': '120.00', 'date': 'February 20, 2024', 'image': 'beau.png'},
        {'id': '879234', 'name': '1x Floral Summer Dress', 'status': 'Canceled', 'total': '120.00', 'date': 'February 20, 2024', 'image': 'shirt.png'}
    ]
    return render_template('myorders.html', orders=sample_orders)

@app.route('/order/<order_id>')
def order_detail(order_id):
    order = {
        'id': order_id,
        'status': 'In Process',
        'items': [
            {'name': 'Zara Classic White Shirt – White', 'quantity': 1, 'price': '28', 'image': 'marita.png'},
            {'name': 'Zara Classic White Shirt – White', 'quantity': 1, 'price': '28', 'image': 'beau.png'}
        ],
        'address': '123-45 Gangnam-daero, Gangnam-gu, Seoul, South Korea, 06050',
        'delivery_option': 'Home Delivery',
        'total': '28',
        'discount': '1.50',
        'delivery_fee': '0.50',
        'tax': '0.80',
        'final_total': '29'
    }
    order['payment_image'] = url_for('static', filename='paypal.png')
    return render_template('order_detail.html', order=order)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
