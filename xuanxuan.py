from flask import Blueprint,render_template,session, redirect, url_for, request as flask_request,jsonify;
xuanxuan_routes = Blueprint('xuanxuan_routes', __name__)


@xuanxuan_routes.route("/",endpoint='index')
def index():
    return render_template('index.html')


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
@xuanxuan_routes.route("/sellitem/<int:step>" ,endpoint='sellitem')
def sellitem(step):
    if step == 1:
        return render_template("sellitem.html")
    else:
        return render_template(f"sellitem{step}.html")
@xuanxuan_routes.route('/search',endpoint='search')
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

@xuanxuan_routes.route('/search_typing', methods=['GET'],endpoint='search_typing')
def search_typing():
    search_input = flask_request.args.get('input', '').lower()
    suggestions = []
    if search_input:
        suggestions = [
            product['name'] for product in dummy_products
            if search_input in product['name'].lower()
        ][:5]
    return jsonify({'suggestions': suggestions})

@xuanxuan_routes.route("/itemsuccess",endpoint='itemsuccess')
def itemsuccess():
    return render_template('itemsuccess.html')

@xuanxuan_routes.route('/product/<int:product_id>',endpoint='product_page')
def product_page(product_id):
    product = dummy_products.get(product_id)
    if not product:
        return "Product not found", 404

    product_copy = product.copy()
    product_copy['id'] = product_id  # add id here

    if product_copy['discounted_price'] is None or product_copy['discounted_price'] >= product_copy['original_price']:
        product_copy['discounted_price'] = product_copy['original_price']

    return render_template('productpage.html', product=product_copy)

@xuanxuan_routes.route('/categories',endpoint='categories_page')
def categories_page():
    return render_template('categories.html', categories=categories)

@xuanxuan_routes.route('/category/<category_name>',endpoint='category_products')
def category_products(category_name):
    category_items = products.get(category_name, [])
    return render_template('category_products.html', category_name=category_name, products=category_items, categories=categories)


@xuanxuan_routes.route('/myprofile',endpoint='myprofile')
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

@xuanxuan_routes.route('/notification',endpoint='notification')
def notification():
    return render_template('notification.html', notifications=notifications)

@xuanxuan_routes.route('/mark_all_read', methods=['POST'],endpoint='mark_all_read')
def mark_all_read():
    for note in notifications:
        note['read'] = True
        note['color'] = 'black'
    return jsonify({'status': 'success'})

@xuanxuan_routes.route('/notification/<int:index>',endpoint='notification_detail')
def notification_detail(index):
    if 0 <= index < len(notifications):
        notifications[index]['read'] = True
        notifications[index]['color'] = 'black'
        return render_template('notification_detail.html', note=notifications[index])
    return "Notification not found", 404

@xuanxuan_routes.route('/myorders',endpoint='my_orders')
def my_orders():
    sample_orders = [
        {'id': '879234', 'name': '1x Floral Summer Dress', 'status': 'Completed', 'total': '120.00', 'date': 'February 20, 2024', 'image': 'marita.png'},
        {'id': '879234', 'name': '1x Floral Summer Dress', 'status': 'In Process', 'total': '120.00', 'date': 'February 20, 2024', 'image': 'beau.png'},
        {'id': '879234', 'name': '1x Floral Summer Dress', 'status': 'Canceled', 'total': '120.00', 'date': 'February 20, 2024', 'image': 'shirt.png'}
    ]
    return render_template('myorders.html', orders=sample_orders)

@xuanxuan_routes.route('/order/<order_id>',endpoint='order_detail')
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

@xuanxuan_routes.route('/cart',endpoint='cart')
def cart():
    return render_template('cart.html')
