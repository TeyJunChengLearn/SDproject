from flask import Blueprint,render_template,session, redirect, url_for, request as flask_request,jsonify;
xuanxuan_routes = Blueprint('xuanxuan_routes', __name__)


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


# @xuanxuan_routes.route('/search_typing', methods=['GET'],endpoint='search_typing')
# def search_typing():
#     search_input = flask_request.args.get('input', '').lower()
#     suggestions = []
#     if search_input:
#         suggestions = [
#             product['name'] for product in dummy_products
#             if search_input in product['name'].lower()
#         ][:5]
#     return jsonify({'suggestions': suggestions})

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
