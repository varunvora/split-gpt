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

# Group endpoints
@app.route('/groups', methods=['POST'])
def create_group():
    data = request.json
    new_group = Group(
        group_id=data['group_id'],
        name=data['name'],
        created_by=data.get('created_by'),
        created_time=datetime.datetime.utcnow()
    )
    session.add(new_group)
    session.commit()
    return jsonify({'message': 'Group created successfully', 'group': new_group.group_id}), 201

@app.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        return jsonify({
            'group_id': group.group_id,
            'name': group.name,
            'created_time': group.created_time,
            'updated_time': group.updated_time,
            'created_by': group.created_by,
            'updated_by': group.updated_by,
            'members': [member.user_id for member in group.members]
        }), 200
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>', methods=['PUT'])
def update_group(group_id):
    data = request.json
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        group.name = data.get('name', group.name)
        group.updated_by = data.get('updated_by', group.updated_by)
        group.updated_time = datetime.datetime.utcnow()
        session.commit()
        return jsonify({'message': 'Group updated successfully'}), 200
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>', methods=['DELETE'])
def delete_group(group_id):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        session.delete(group)
        session.commit()
        return jsonify({'message': 'Group deleted successfully'}), 200
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>/members', methods=['POST'])
def add_member_to_group(group_id):
    data = request.json
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        user = session.query(User).filter(User.user_id == data['user_id']).first()
        if user:
            group.members.append(user)
            session.commit()
            return jsonify({'message': 'Member added to group successfully'}), 200
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>/members/<user_id>', methods=['DELETE'])
def remove_member_from_group(group_id, user_id):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user and user in group.members:
            group.members.remove(user)
            session.commit()
            return jsonify({'message': 'Member removed from group successfully'}), 200
        return jsonify({'message': 'User not found in group'}), 404
    return jsonify({'message': 'Group not found'}), 404

# Expense endpoints
@app.route('/groups/<group_id>/expenses', methods=['POST'])
def create_expense(group_id):
    data = request.json
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        new_expense = Expense(
            expense_id=data['expense_id'],
            group_id=group_id,
            amount=data['amount'],
            description=data['description'],
            created_by=data.get('created_by'),
            created_time=datetime.datetime.utcnow()
        )
        session.add(new_expense)
        for split in data['splits']:
            new_split = ExpenseSplit(
                split_id=split['split_id'],
                expense_id=new_expense.expense_id,
                user_id=split['user_id'],
                amount=split['amount'],
                split_type=split['split_type']
            )
            session.add(new_split)
        session.commit()
        return jsonify({'message': 'Expense created successfully', 'expense': new_expense.expense_id}), 201
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>/expenses/<expense_id>', methods=['GET'])
def get_expense(group_id, expense_id):
    expense = session.query(Expense).filter(Expense.expense_id == expense_id, Expense.group_id == group_id).first()
    if expense:
        splits = session.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).all()
        split_details = [{
            'split_id': split.split_id,
            'user_id': split.user_id,
            'amount': split.amount,
            'split_type': split.split_type.value
        } for split in splits]
        return jsonify({
            'expense_id': expense.expense_id,
            'group_id': expense.group_id,
            'amount': expense.amount,
            'description': expense.description,
            'created_time': expense.created_time,
            'updated_time': expense.updated_time,
            'created_by': expense.created_by,
            'updated_by': expense.updated_by,
            'splits': split_details
        }), 200
    return jsonify({'message': 'Expense not found'}), 404

@app.route('/groups/<group_id>/expenses/<expense_id>', methods=['PUT'])
def update_expense(group_id, expense_id):
    data = request.json
    expense = session.query(Expense).filter(Expense.expense_id == expense_id, Expense.group_id == group_id).first()
    if expense:
        expense.amount = data.get('amount', expense.amount)
        expense.description = data.get('description', expense.description)
        expense.updated_by = data.get('updated_by', expense.updated_by)
        expense.updated_time = datetime.datetime.utcnow()
        session.commit()
        return jsonify({'message': 'Expense updated successfully'}), 200
    return jsonify({'message': 'Expense not found'}), 404

@app.route('/groups/<group_id>/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(group_id, expense_id):
    expense = session.query(Expense).filter(Expense.expense_id == expense_id, Expense.group_id == group_id).first()
    if expense:
        session.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()
        session.delete(expense)
        session.commit()
        return jsonify({'message': 'Expense deleted successfully'}), 200
    return jsonify({'message': 'Expense not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
