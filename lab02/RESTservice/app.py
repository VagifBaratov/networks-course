
import os
import time
from flask import Flask, request, jsonify, send_from_directory

UPLOAD_FOLDER = "downloads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

products = {}
next_id = 1

def generate_id():
    global next_id
    current_id = next_id
    next_id += 1
    return current_id

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/product', methods=['POST'])
def create_product():
    global next_id
    
    data = request.get_json()
    
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({'error': 'Incorrect product data'}), 400
    
    product_id = generate_id()
    new_product = {
        'id': product_id,
        'name': data['name'],
        'description': data['description'],
    }
    
    products[product_id] = new_product
    
    return jsonify(new_product), 201


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    if product_id not in products:
        return jsonify({'error': f'Product with id {product_id} not found'}), 404

    return jsonify(products[product_id])


@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if product_id not in products:
        return jsonify({'error': f'Product with id {product_id} not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'The request body cannot be empty'}), 400
    
    product = products[product_id]
    if 'name' in data:
        product['name'] = data['name']
    if 'description' in data:
        product['description'] = data['description']
    
    products[product_id] = product
    
    return jsonify(product)


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if product_id not in products:
        return jsonify({'error': f'Product with id {product_id} not found'}), 404
    
    deleted_product = products.pop(product_id)
    
    return jsonify(deleted_product)


@app.route('/products', methods=['GET'])
def get_all_products():
    products_list = list(products.values())
    return jsonify(products_list)

@app.route('/product/<int:product_id>/image', methods=['POST'])
def upload_icon(product_id):
    if product_id not in products:
        return jsonify({'error': f'Product with id {product_id} not found'}), 404

    if 'icon' not in request.files:
        return jsonify({'error': 'Attach an image'}), 400
    
    icon_file = request.files['icon']
    filename = icon_file.filename
    if not allowed_file(filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = f"prod_{product_id}_{int(time.time())}_{icon_file.filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    icon_file.save(file_path)

    products[product_id]['icon'] = filename
    return jsonify(products[product_id]), 200

@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_icon(product_id):
    if product_id not in products:
        return jsonify({'error': f'Product with id {product_id} not found'}), 404
    
    product = products[product_id]

    if 'icon' not in product:
        return jsonify({'error': f'No icon assigned for product with id {product_id}'}), 400
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], product['icon'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)