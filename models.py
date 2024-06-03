from sqlalchemy import Column, String, Float, DateTime, Table, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import enum

Base = declarative_base()

class SplitType(enum.Enum):
    PAID = "PAID"
    OWES = "OWES"

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)              # Unique identifier for the user
    name = Column(String, nullable=False)                   # Full name of the user
    email = Column(String, nullable=False, unique=True)     # Email address of the user
    created_time = Column(DateTime, default=datetime.datetime.utcnow)  # Timestamp of when the user was created
    updated_time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # Timestamp of when the user was last updated
    created_by = Column(String)                             # User who created this record
    updated_by = Column(String)                             # User who last updated this record

class Group(Base):
    __tablename__ = 'groups'
    group_id = Column(String, primary_key=True)                 # Unique identifier for the group
    name = Column(String, nullable=False)                       # Name of the group
    created_time = Column(DateTime, default=datetime.datetime.utcnow)  # Timestamp of when the group was created
    updated_time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # Timestamp of when the group was last updated
    created_by = Column(String)                                 # User who created this record
    updated_by = Column(String)                                 # User who last updated this record

    # Many-to-Many relationship with users
    members = relationship('User', secondary='group_members')

# Association table for the many-to-many relationship
group_members = Table(
    'group_members', Base.metadata,
    Column('user_id', String, ForeignKey('users.user_id'), primary_key=True),
    Column('group_id', String, ForeignKey('groups.group_id'), primary_key=True)
)

class Expense(Base):
    __tablename__ = 'expenses'
    expense_id = Column(String, primary_key=True)               # Unique identifier for the expense
    group_id = Column(String, ForeignKey('groups.group_id'), nullable=False)  # Identifier of the group the expense belongs to
    amount = Column(Float, nullable=False)                      # Total amount of the expense
    description = Column(String, nullable=False)                # Description of the expense
    created_time = Column(DateTime, default=datetime.datetime.utcnow)  # Timestamp of when the expense was created
    updated_time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # Timestamp of when the expense was last updated
    created_by = Column(String)                                 # User who created this record
    updated_by = Column(String)                                 # User who last updated this record

    # Relationships
    splits = relationship('ExpenseSplit', back_populates='expense')

class ExpenseSplit(Base):
    __tablename__ = 'expense_splits'
    split_id = Column(String, primary_key=True)                 # Unique identifier for the split
    expense_id = Column(String, ForeignKey('expenses.expense_id'), nullable=False)  # Identifier of the expense
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)  # User involved in this split
    amount = Column(Float, nullable=False)                      # Amount paid or owed by the user
    split_type = Column(Enum(SplitType), nullable=False)        # Split type: PAID or OWES

    # Relationships
    expense = relationship('Expense', back_populates='splits')
    user = relationship('User')
