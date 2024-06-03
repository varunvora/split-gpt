from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Group, Expense, ExpenseSplit  # Importing the models defined earlier
import datetime

app = Flask(__name__)

# Database setup
engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'UP'}), 200

# User endpoints
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(
        user_id=data['user_id'],
        name=data['name'],
        email=data['email'],
        created_by=data.get('created_by'),
        created_time=datetime.datetime.utcnow()
    )
    session.add(new_user)
    session.commit()
    return jsonify({'message': 'User created successfully', 'user': new_user.user_id}), 201

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        return jsonify({
            'user_id': user.user_id,
            'name': user.name,
            'email': user.email,
            'created_time': user.created_time,
            'updated_time': user.updated_time,
            'created_by': user.created_by,
            'updated_by': user.updated_by
        }), 200
    return jsonify({'message': 'User not found'}), 404

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.updated_by = data.get('updated_by', user.updated_by)
        user.updated_time = datetime.datetime.utcnow()
        session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
