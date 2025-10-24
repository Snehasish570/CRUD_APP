from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Item
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
CORS(app)  # ✅ Allows React frontend to access Flask API

# ✅ PostgreSQL Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mohuda%401234@localhost:5432/flask_crud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialize Database
db.init_app(app)

with app.app_context():
    db.create_all()

# ✅ ROUTES

# Get all items
@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([i.to_dict() for i in items])

# Get single item
@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

# Create item (with unique email check)
@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    name = data.get('name')
    mail = data.get('mail')

    if not name or not mail:
        return jsonify({'error': 'Name and Email are required'}), 400

    new_item = Item(name=name, mail=mail)
    db.session.add(new_item)

    try:
        db.session.commit()
        return jsonify(new_item.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400

# Update item (with unique email handling)
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()

    item.name = data.get('name', item.name)
    item.mail = data.get('mail', item.mail)

    try:
        db.session.commit()
        return jsonify(item.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400

# Delete item
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'result': True, 'message': 'Item deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
