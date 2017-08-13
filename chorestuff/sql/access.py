from ..common import *
from .decl import *

@Singleton
class DataHandler:
  def __init__(self):
    self.session = None
    self.engine = None

  """
    Database-related functions.
  """

  def Bind(self):
    self.engine = create_engine('sqlite:///%s' % app.config['DATABASE'])
    Base.metadata.bind = self.engine

    self.DBSession = sessionmaker(bind=self.engine)
    self.session = self.DBSession()

  def Create(self):
    self.engine = create_engine('sqlite:///%s' % app.config['DATABASE'])
    Base.metadata.create_all(self.engine)
    Base.metadata.bind = self.engine

    self.DBSession = sessionmaker(bind=self.engine)
    self.session = self.DBSession()

  def Commit(self):
    if self.session:
      self.session.commit()

  def Quit(self):
    if self.session:
      self.session.commit()
      self.session.close()

  """
    Chores manipulation.
  """

  def AddChore(self, name, **kwargs):
    chore = self.session.query(Chore).filter(Chore.name == name).first()

    if chore: return chore

    new_chore = Chore(added = datetime.now(), name = name, **kwargs)
    self.session.add(new_chore)

    return new_chore

  def RemoveChore(self, id):
    chore = self.session.query(Chore).filter(Chore.id == id).first()
    if chore:
      self.session.delete(chore)

  def GetAllChores(self):
    return self.session.query(Chore).order_by(Chore.name.asc()).all()

  def GetChore(self, id):
    chore = self.session.query(Chore).filter(Chore.id == id).first()

    if chore == None:
      print('Warning getting chore: id not found.')

    return chore

  """
    Tenant manipulation
  """

  def AddTenant(self, **kwargs):
    new_tenant = Tenant(added = datetime.now(), **kwargs)
    self.session.add(new_tenant)

    return new_tenant

  def RemoveTenant(self, id):
    tenant = self.session.query(Tenant).filter(Tenant.id == id).first()

    if tenant: self.session.delete(tenant)

  def GetAllTenants(self, sorted = False):
    if sorted:
      return self.session.query(Tenant).order_by(Tenant.name.asc()).all()

    return self.session.query(Tenant).all()

  def GetLivingTenants(self, sorted = False):
    if sorted:
      return self.session.query(Tenant).filter(Tenant.is_living == True).order_by(Tenant.name.asc()).all()

    return self.session.query(Tenant).filter(Tenant.is_living == True).all()

  def GetTenant(self, id):
    tenant = self.session.query(Tenant).filter(Tenant.id == id).first()

    if tenant == None:
      print('Warning getting tenant: id not found.')

    return tenant

  """
    Assignments manipulation
  """
  def GetBundleDate(self, date):
    return date - timedelta(days=date.isocalendar()[2] - 1)

  def AddAssignmentBundle(self, date, init = True, chores = {}, extra_chores = []):
    # Chores is a dictionary specifying chores: chores[tenant.id] = chore
    bundle_date = self.GetBundleDate(date)
    new_bundle = AssignmentBundle(added = datetime.now(), date = bundle_date)

    if init:
      self.InitAssignmentBundle(new_bundle, chores, extra_chores)

    self.session.add(new_bundle)

    return new_bundle

  def InitAssignmentBundle(self, new_bundle, chores = {}, extra_chores = []):
    for tenant in self.GetLivingTenants():
      new_assignment = Assignment(
        added = datetime.now(),
        tenant = tenant,
        bundle = new_bundle,
        is_tenant_home = tenant.is_home,
        chore = chores[tenant.id] if tenant.id in chores else None
      )
      self.session.add(new_assignment)

    for chore in extra_chores:
      new_assignment = Assignment(added = datetime.now(), tenant = None, bundle = new_bundle, chore = chore)
      self.session.add(new_assignment)

  def GetAllAssignmentBundles(self, sorted = False):
    if sorted:
      return self.session.query(AssignmentBundle).order_by(AssignmentBundle.date.desc()).all()

    return self.session.query(AssignmentBundle).all()

  def GetAssignmentBundle(self, id):
    bundle = self.session.query(AssignmentBundle).filter(AssignmentBundle.id == id).first()

    if bundle == None:
      print('Warning getting assignment bundle: id not found.')

    return bundle

  def GetAssignmentBundleByDate(self, date):
    bundle_date = self.GetBundleDate(date)
    bundle = self.session.query(AssignmentBundle).filter(bundle_date).first()

    if bundle == None:
      print('Warning getting assignment bundle: date not found.')

    return bundle

  def RemoveAssignmentBundle(self, id):
    bundle = self.session.query(AssignmentBundle).filter(AssignmentBundle.id == id).first()

    if bundle: self.session.delete(bundle)

  def RemoveAssignment(self, id):
    assignment = self.session.query(Assignment).filter(Assignment.id == id).first()

    if assignment: self.session.delete(assignment)

  def SetAssignmentsChores(self, bundle, chores):
    """
      Sets the chore for each assignment. chores is a dictionary
      of the form chores[tenant.id] = chore.
    """

    for assignment in bundle.assignments:
      if assignment.tenant:
        assignment.chore = chores[assignment.tenant.id] if assignment.tenant.id in chores else assignment.chore

  def SetTenantIsHome(self, bundle, home_dict):
    for assignment in bundle.assignments:
      if assignment.tenant:
        if assignment.tenant.id in home_dict:
          assignment.is_tenant_home = home_dict[assignment.tenant.id]

  def AddExtraChores(self, bundle, extra_chores):
    existing_chores = [assignment.chore.id for assignment in bundle.assignments if assignment.chore]
    for chore in extra_chores:
      if not chore.id in existing_chores:
        new_assignment = Assignment(added = datetime.now(), tenant = None, bundle = bundle, chore = chore)
        self.session.add(new_assignment)

  def CompleteAssignment(self, assignment, **kwargs):
    new_completion = CompletedAssignment(added = datetime.now(), assignment = assignment, **kwargs)
    self.session.add(new_completion)
    return new_completion

  def CycleBundle(self, bundle_list, repeat = 0):
    if repeat:
      if isinstance(bundle_list, list):
        bundle = bundle_list[-1]
      else:
        bundle = bundle_list
        bundle_list = [bundle_list]

      old_assignments = sorted([assignment for assignment in bundle.assignments if assignment.tenant], key = lambda a: a.tenant.name, reverse = True)

      chores = {}

      for i, assignment in enumerate(old_assignments):
        chores[assignment.tenant.id] = old_assignments[i+1 if i+1 < len(old_assignments) else 0].chore

      new_bundle = self.AddAssignmentBundle(bundle.date + timedelta(days=7), chores = chores)

      bundle_list.append(new_bundle)

      return self.CycleBundle(bundle_list, repeat = repeat - 1)
    else:
      return bundle_list

  """
    Billing manipulation
  """

  def AddBill(self, end_date, b_date = None, **kwargs):
    if b_date:
      # If b_date is defined.
      begin_date = b_date
    else:
      last_bill = self.session.query(Bill).order_by(Bill.end_date.desc()).first()

      # If there is a last bill we can use.
      if last_bill:
        begin_date = last_bill.end_date + timedelta(days=1)

      else:
        # Otherwise start from the beginning of time.
        begin_date = date(year=1970, month=1, day=1)

    if not 'bank_account' in kwargs:
      bank_account = self.session.query(BankAccount).first()
      new_bill = Bill(added = datetime.now(), begin_date = begin_date, end_date = end_date, bank_account = bank_account, **kwargs)
    else:
      new_bill = Bill(added = datetime.now(), begin_date = begin_date, end_date = end_date, **kwargs)

    self.session.add(new_bill)
    self.InitBillEntries(new_bill)
    return new_bill

  def InitBillEntries(self, new_bill):
    living_tenants = self.GetLivingTenants()

    expenses = self.session.query(Transaction).filter(and_(Transaction.date.between(new_bill.begin_date, new_bill.end_date), Transaction.type == TransactionType.expense)).all()

    # Computing shared expenses.
    new_bill.shared_expenses = sum([expense.amount for expense in expenses]) / len(living_tenants)
    new_bill_entries = {}

    # Initialize bill entries.
    for tenant in living_tenants:
      bill_transactions = self.session.query(Transaction).filter(and_(Transaction.date.between(new_bill.begin_date, new_bill.end_date), Transaction.type == TransactionType.bill, Transaction.tenant == tenant)).all()

      payments = self.session.query(Transaction).filter(and_(Transaction.date.between(new_bill.begin_date, new_bill.end_date), Transaction.tenant == tenant), Transaction.type == TransactionType.payment).all()

      # Previous debt: get the bill entry for this tenant, associated with
      # the latest bill by date.
      # Then, we add any other bills in this time range.
      last_bill_entry = self.session.query(BillEntry).filter(BillEntry.tenant == tenant).order_by(BillEntry.date.desc()).first()

      new_bill_entries[tenant.id] = BillEntry(added = datetime.now(), date = new_bill.end_date, tenant = tenant, bill = new_bill)

      # Add entry to session.
      self.session.add(new_bill_entries[tenant.id])

      # Add last debts.
      new_bill_entries[tenant.id].prev_debt = last_bill_entry.total if last_bill_entry else 0.0
      new_bill_entries[tenant.id].prev_debt += sum([transaction.amount for transaction in bill_transactions])

      # Compute payments.
      new_bill_entries[tenant.id].paid = -sum([transaction.amount for transaction in payments])

    # Computing personal expenses.
    for expense in expenses:
      new_bill_entries[expense.tenant.id].p_expenses -= expense.amount

    # Computing now the cleaning cost and discounts.
    bundles = self.session.query(AssignmentBundle).filter(AssignmentBundle.date.between(new_bill.begin_date, new_bill.end_date)).all()

    for bundle in bundles:
      for assignment in bundle.assignments:
        # Add chore value if tenant is home (and it's defined).
        if assignment.is_tenant_home and assignment.tenant and assignment.chore:
          new_bill_entries[assignment.tenant.id].cleaning += assignment.chore.value

        # Add completed chores' values.
        for completion in assignment.completions:
          if assignment.chore:
            new_bill_entries[completion.tenant.id].discount -= assignment.chore.value

    # Compute contribution for managers.
    manager_contribution = 0.0
    for tenant in living_tenants:
      if tenant.is_manager:
        new_bill_entries[tenant.id].contribution = - new_bill_entries[tenant.id].cleaning
        manager_contribution += new_bill_entries[tenant.id].cleaning

    manager_contribution /= len(self.session.query(Tenant).filter(and_(Tenant.is_living == True, Tenant.is_manager == False)).all())

    # Contribution for the rest.
    for tenant in living_tenants:
      if not tenant.is_manager:
        new_bill_entries[tenant.id].contribution = manager_contribution

    # Final calculation
    for (key, entry) in new_bill_entries.items():
      # Compute subtotal: amount to pay considering only this bill.
      entry.subtotal = entry.contribution + entry.cleaning + entry.discount + entry.p_expenses + new_bill.recurring + new_bill.shared_expenses

      # Total amount to pay considering last bill's total, paid amounts and current bill.
      entry.total = entry.prev_debt + entry.paid + entry.subtotal

    return new_bill_entries

  def UpdateBillEntries(self, bill):
    # Mainly for updating recurring and shared expenses.
    for entry in bill.entries:
      entry.subtotal = entry.contribution + entry.cleaning - entry.discount - entry.p_expenses + bill.recurring + bill.shared_expenses
      entry.total = entry.prev_debt - entry.paid + entry.subtotal

  def ComputeTenantBalance(self, tenant):
    balance = 0.0

    # Get last bill's total.
    last_bill = self.session.query(BillEntry).filter(BillEntry.tenant == tenant).order_by(BillEntry.date.desc()).first()

    if last_bill:
      balance += last_bill.total

    # Add any extra transaction bills since the last actual bill, or since beginning of time.
    bills = self.session.query(Transaction).filter(and_(Transaction.date.between(last_bill.end_date if last_bill else date(year=1970, month=1, day=1), date.today()), Transaction.type == TransactionType.bill)).all()

    balance += sum([bill.amount for bill in bills])

    # Add payments made since then.
    # If there is no previous bill, considering everything since the beginning of time.
    payments = self.session.query(Transaction).filter(and_(Transaction.date.between(last_bill.end_date if last_bill else date(year=1970, month=1, day=1), date.today()), Transaction.type == TransactionType.payment)).all()

    balance -= sum([payment.amount for payment in payments])

    return balance

  """
    Transaction manipulation
  """

  def AddTransaction(self, **kwargs):
    new_transaction = Transaction(added = datetime.now(), **kwargs)
    self.session.add(new_transaction)

    return new_transaction

  """
    Bank account manipulation
  """

  def AddBankAccount(self, **kwargs):
    new_bank_account = BankAccount(added = datetime.now(), **kwargs)
    self.session.add(new_bank_account)

    return new_bank_account

  def GetBankAccount(self, id):
    bank_account = self.session.query(BankAccount).filter(BankAccount.id == id).first()

    if bank_account == None:
      print('Warning getting bank account: id not found.')

    return bank_account

  def RemoveBankAccount(self, id):
    bank_account = self.session.query(BankAccount).filter(BankAccount.id == id).first()

    if bank_account: self.session.delete(bank_account)

