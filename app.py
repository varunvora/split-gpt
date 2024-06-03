from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Group, Expense, ExpenseSplit
import datetime

app = Flask(__name__)

# Database setup
DATABASE_URL = 'sqlite:///app.db'
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Decorator for handling exceptions
def handle_exceptions(f):
    import functools
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            method_name = f.__name__
            logging.error(f"Error in {method_name}: {str(e)}")
            return jsonify({'message': f"Error in {method_name}", 'error': str(e)}), 500
    return decorated_function

# Health check endpoint
@app.route('/health', methods=['GET'])
@handle_exceptions
def health_check():
    return jsonify({'status': 'UP'}), 200

# User endpoints
@app.route('/users', methods=['POST'])
@handle_exceptions
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
    logging.info(f"User created: {new_user.user_id}")
    return jsonify({'message': 'User created successfully', 'user': new_user.user_id}), 201

@app.route('/users/<user_id>', methods=['GET'])
@handle_exceptions
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
@handle_exceptions
def update_user(user_id):
    data = request.json
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        user.updated_by = data.get('updated_by', user.updated_by)
        user.updated_time = datetime.datetime.utcnow()
        session.commit()
        logging.info(f"User updated: {user.user_id}")
        return jsonify({'message': 'User updated successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@app.route('/users/<user_id>', methods=['DELETE'])
@handle_exceptions
def delete_user(user_id):
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        session.delete(user)
        session.commit()
        logging.info(f"User deleted: {user.user_id}")
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

# Group endpoints
@app.route('/groups', methods=['POST'])
@handle_exceptions
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
    logging.info(f"Group created: {new_group.group_id}")
    return jsonify({'message': 'Group created successfully', 'group': new_group.group_id}), 201

@app.route('/groups/<group_id>', methods=['GET'])
@handle_exceptions
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
@handle_exceptions
def update_group(group_id):
    data = request.json
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        group.name = data.get('name', group.name)
        group.updated_by = data.get('updated_by', group.updated_by)
        group.updated_time = datetime.datetime.utcnow()
        session.commit()
        logging.info(f"Group updated: {group.group_id}")
        return jsonify({'message': 'Group updated successfully'}), 200
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>', methods=['DELETE'])
@handle_exceptions
def delete_group(group_id):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        session.delete(group)
        session.commit()
        logging.info(f"Group deleted: {group.group_id}")
        return jsonify({'message': 'Group deleted successfully'}), 200
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>/members', methods=['POST'])
@handle_exceptions
def add_member_to_group(group_id):
    data = request.json
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        user = session.query(User).filter(User.user_id == data['user_id']).first()
        if user:
            group.members.append(user)
            session.commit()
            logging.info(f"Member added to group: {user.user_id} to {group.group_id}")
            return jsonify({'message': 'Member added to group successfully'}), 200
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>/members/<user_id>', methods=['DELETE'])
@handle_exceptions
def remove_member_from_group(group_id, user_id):
    group = session.query(Group).filter(Group.group_id == group_id).first()
    if group:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user and user in group.members:
            group.members.remove(user)
            session.commit()
            logging.info(f"Member removed from group: {user.user_id} from {group.group_id}")
            return jsonify({'message': 'Member removed from group successfully'}), 200
        return jsonify({'message': 'User not found in group'}), 404
    return jsonify({'message': 'Group not found'}), 404

# Expense endpoints
@app.route('/groups/<group_id>/expenses', methods=['POST'])
@handle_exceptions
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
        logging.info(f"Expense created: {new_expense.expense_id}")
        return jsonify({'message': 'Expense created successfully', 'expense': new_expense.expense_id}), 201
    return jsonify({'message': 'Group not found'}), 404

@app.route('/groups/<group_id>/expenses/<expense_id>', methods=['GET'])
@handle_exceptions
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
@handle_exceptions
def update_expense(group_id, expense_id):
    data = request.json
    expense = session.query(Expense).filter(Expense.expense_id == expense_id, Expense.group_id == group_id).first()
    if expense:
        expense.amount = data.get('amount', expense.amount)
        expense.description = data.get('description', expense.description)
        expense.updated_by = data.get('updated_by', expense.updated_by)
        expense.updated_time = datetime.datetime.utcnow()
        session.commit()
        logging.info(f"Expense updated: {expense.expense_id}")
        return jsonify({'message': 'Expense updated successfully'}), 200
    return jsonify({'message': 'Expense not found'}), 404

@app.route('/groups/<group_id>/expenses/<expense_id>', methods=['DELETE'])
@handle_exceptions
def delete_expense(group_id, expense_id):
    expense = session.query(Expense).filter(Expense.expense_id == expense_id, Expense.group_id == group_id).first()
    if expense:
        session.query(ExpenseSplit).filter(ExpenseSplit.expense_id == expense_id).delete()
        session.delete(expense)
        session.commit()
        logging.info(f"Expense deleted: {expense.expense_id}")
        return jsonify({'message': 'Expense deleted successfully'}), 200
    return jsonify({'message': 'Expense not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
