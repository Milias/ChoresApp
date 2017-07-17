# -*- coding: utf8 -*-
import os
import sys
import enum
import uuid
from datetime import datetime, date

from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey, Binary, Boolean, Float, types, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class UUID(types.TypeDecorator):
  impl = Binary

class TransactionType(enum.Enum):
  expense = 1
  payment = 2
  bill = 4
  other = 8

"""
  Tenant information
"""

class Tenant(Base):
  __tablename__ = 'tenants'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)
  added = Column(DateTime, nullable = False, default = datetime.now)

  short_name = Column(String(250), default = '', nullable = False)
  full_name = Column(String(250), default = '', nullable = False)
  email = Column(String(250), default = '', nullable = False)
  room = Column(Integer)

  balance_offset = Column(Float, default = 0.0, nullable = False)
  contribution = Column(Float, default = 0.0, nullable = False)

  living = Column(Boolean, default = True, nullable = False)
  home = Column(Boolean, default = True, nullable = False)

"""
  Chore information
"""

class Chore(Base):
  __tablename__ = 'chores'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)
  added = Column(DateTime, nullable = False, default = datetime.now)

  name = Column(String(250), default = '', nullable = False)
  description = Column(Text, default = '')
  value = Column(Float, default = 2.5, nullable = False)

"""
  Assignments information
"""

class AssignmentBundle(Base):
  __tablename__ = 'assignment_bundles'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)
  assigned = Column(DateTime, nullable = False, default = datetime.now)

  due = Column(Date, nullable = False, default = date.today)

class Assignment(Base):
  __tablename__ = 'assignments'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)

  tenant_id = Column(UUID(), ForeignKey('tenants.id'))
  chore_id = Column(UUID(), ForeignKey('chores.id'), nullable = False)

  tenant = relationship(Tenant)
  chore = relationship(Chore)

  bundle_id = Column(UUID(), ForeignKey('assignment_bundles.id'), nullable = False)
  bundle = relationship(AssignmentBundle)

  tenant_is_home = Column(Boolean, default = True)

class CompletedAssignment(Base):
  __tablename__ = 'completed_assignments'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)
  date = Column(Date, nullable = False, default = date.today)

  tenant_id = Column(UUID(), ForeignKey('tenants.id'))
  tenant = relationship(Tenant)

  assignment_id = Column(UUID(), ForeignKey('assignments.id'), nullable = False)
  assignment = relationship(Assignment)

"""
  Billing information
"""

class Bill(Base):
  __tablename__ = 'bills'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)
  begin_date = Column(Date, default = date.today, nullable = False)
  end_date = Column(Date, default = date.today, nullable = False)

  recurring = Column(Float, default = 0.0, nullable = False)
  s_expenses = Column(Float, default = 0.0, nullable = False)

class BillEntry(Base):
  __tablename__ = 'bill_entries'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)

  tenant_id = Column(UUID(), ForeignKey('tenants.id'))
  tenant = relationship(Tenant)

  bill_id = Column(UUID(), ForeignKey('bills.id'))
  bill = relationship(Bill)

  contribution = Column(Float, nullable = False)
  p_expenses = Column(Float, nullable = False)
  cleaning = Column(Float, nullable = False)
  discount = Column(Float, nullable = False)
  subtotal = Column(Float, nullable = False)

class BankAccount(Base):
  __tablename__ = 'bank_accounts'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)
  bank_name = Column(String(250), default = '', nullable = False)
  account = Column(String(250), default = '', nullable = False)
  holder = Column(String(250), default = '', nullable = False)
  location = Column(String(250), default = '', nullable = False)

"""
  Transaction information
"""

class Transaction(Base):
  __tablename__ = 'transactions'

  id = Column(UUID(), primary_key = True, default = uuid.uuid4)
  type = Column(Enum(TransactionType), nullable = False)
  date = Column(Date, nullable = False, default = date.today)

  amount = Column(Float, nullable = False, default = 0.0)
  description = Column(Text, default = '')

  tenant_id = Column(UUID(), ForeignKey('tenants.id'))
  tenant = relationship(Tenant)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///config/database.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

