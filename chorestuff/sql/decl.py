from ..common import *

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

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  name = Column(String(256), default = '', nullable = False)
  full_name = Column(String(256), default = '')
  email = Column(String(256), default = '')
  room = Column(Integer)

  # Contribution per month (regardless of weeks)
  contribution = Column(Float, default = 0.0, nullable = False)

  is_living = Column(Boolean, default = True, nullable = False)
  is_home = Column(Boolean, default = True, nullable = False)

"""
  Chore information
"""

class Chore(Base):
  __tablename__ = 'chores'

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  name = Column(String(256), default = '', nullable = False)
  description = Column(Text, default = '')
  value = Column(Float, default = 2.50, nullable = False)

"""
  Assignments information
"""

class AssignmentBundle(Base):
  __tablename__ = 'assignment_bundles'

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  date = Column(Date, default = date.today, nullable = False)

  assignments = relationship('Assignment', back_populates = 'bundle')

class Assignment(Base):
  __tablename__ = 'assignments'

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  tenant_id = Column(Integer, ForeignKey('tenants.id'))
  tenant = relationship(Tenant)

  chore_id = Column(Integer, ForeignKey('chores.id'))
  chore = relationship(Chore)

  bundle_id = Column(Integer, ForeignKey('assignment_bundles.id'))
  bundle = relationship('AssignmentBundle', back_populates = 'assignments')

  completions = relationship('CompletedAssignment', back_populates = 'assignment')

  is_tenant_home = Column(Boolean, default = True)

class CompletedAssignment(Base):
  __tablename__ = 'completed_assignments'

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  date = Column(Date, default = date.today)

  tenant_id = Column(Integer, ForeignKey('tenants.id'))
  tenant = relationship(Tenant)

  assignment_id = Column(Integer, ForeignKey('assignments.id'))
  assignment = relationship('Assignment', back_populates = 'completions')

"""
  Billing information
"""

class Bill(Base):
  __tablename__ = 'bills'

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  begin_date = Column(Date, default = date.today, nullable = False)
  end_date = Column(Date, default = date.today, nullable = False)

  recurring = Column(Float, default = 0.0)
  shared_expenses = Column(Float, default = 0.0)

  entries = relationship('BillEntry', back_populates = 'bill')

class BillEntry(Base):
  __tablename__ = 'bill_entries'

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  tenant_id = Column(Integer, ForeignKey('tenants.id'))
  tenant = relationship(Tenant)

  bill_id = Column(Integer, ForeignKey('bills.id'))
  bill = relationship('Bill', back_populates = 'entries')

  contribution = Column(Float, default = 0.0)
  p_expenses = Column(Float, default = 0.0)
  cleaning = Column(Float, default = 0.0)
  discount = Column(Float, default = 0.0)
  subtotal = Column(Float, default = 0.0)

  prev_debt = Column(Float, default = 0.0)
  paid = Column(Float, default = 0.0)
  total = Column(Float, default = 0.0)

class BankAccount(Base):
  __tablename__ = 'bank_accounts'

  id = Column(Integer, primary_key = True)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  bank_name = Column(String(256), default = '', nullable = False)
  account = Column(String(256), default = '', nullable = False)
  holder = Column(String(256), default = '', nullable = False)
  location = Column(String(256), default = '', nullable = False)

"""
  Transaction information
"""

class Transaction(Base):
  __tablename__ = 'transactions'

  id = Column(Integer, primary_key = True)
  type = Column(Enum(TransactionType), nullable = False)
  added = Column(DateTime, nullable = False, default = datetime.now)
  edited = Column(DateTime, nullable = False, default = datetime.now, onupdate = datetime.now)

  date = Column(Date, default = date.today, nullable = False)

  amount = Column(Float, nullable = False, default = 0.0)
  description = Column(Text, default = '')

  tenant_id = Column(Integer, ForeignKey('tenants.id'))
  tenant = relationship(Tenant)

