from ..common import *
from ..sql import *
from ..texport import *

class FormEditTransaction(RedirectForm):
  transaction_id = HiddenField('Id:')
  type = SelectField('Type:', default = 1, choices = [(1, 'Expense'), (2, 'Payment'), (4, 'Bill'), (8, 'Other')], coerce=int, validators=[InputRequired()])
  tenant = SelectField('Tenant:', choices = [], coerce=int, validators=[Optional()])
  description = TextAreaField('Description:', validators=[Optional()])
  date = DateField('Date:', default = lambda: date.today() - timedelta(days=date.today().isocalendar()[2] - 1), validators = [InputRequired()])
  amount = DecimalField('Amount:', places = 2, validators=[InputRequired()])

class FormEditBill(RedirectForm):
  bill_id = HiddenField('Id:')

  save_bill = BooleanField('Save bill: ', default=False)
  begin_date = DateField('Start date:', default = lambda: date.today() - timedelta(weeks=8), validators = [InputRequired()])
  end_date = DateField('End date:', default = lambda: date.today(), validators = [InputRequired()])
  recurring = DecimalField('Recurring:', places = 2, validators=[InputRequired()])

  #entry_list = FieldList(FormField(FormEditAssignment))

@app.route('/billing/transactions', methods = ('GET', 'POST'))
def BillingTransactions():
  dh = get_session()

  transactions = dh.GetAllTransactions()
  t_types = {TransactionType.expense: 'Expense', TransactionType.payment: 'Payment', TransactionType.bill: 'Bill', TransactionType.other: 'Other'}

  return render_template('billing_transactions.html', transactions = transactions, t_types = t_types)

@app.route('/billing/transactions/edit', defaults = {'transaction_id': 0}, methods = ('GET', 'POST'))
@app.route('/billing/transactions/edit/<int:transaction_id>', methods = ('GET', 'POST'))
def BillingTransactionsEdit(transaction_id):
  dh = get_session()
  form = FormEditTransaction()

  living_tenants = dh.GetAllTenants(sorted = True)
  tenants_choices = [(tenant.id, tenant.name) for tenant in living_tenants]

  form.tenant.choices = tenants_choices

  transaction = None
  if transaction_id:
    transaction = dh.GetTransaction(transaction_id)
    if transaction:
      for attr in (('transaction_id', 'id'), 'description', 'date', 'amount'):
        setattr(getattr(form, attr[0] if isinstance(attr, tuple) else attr), 'data', getattr(transaction, attr[1] if isinstance(attr, tuple) else attr))

      form.tenant.data = transaction.tenant.id
      form.type.data = TransactionTypeDictInv[transaction.type]

  if form.validate_on_submit():
    transaction = dh.GetTransaction(form.transaction_id.data)
    if transaction == None:
      transaction = dh.AddTransaction(tenant = dh.GetTenant(form.tenant.data), type = TransactionTypeDict[form.type.data], date = form.date.data, description = form.description.data, amount = form.amount.data)
      flash('Transaction added.', 'success')
    else:
      for attr in (('transaction_id', 'id'), 'description', 'date', 'amount'):
        setattr(transaction, attr[1] if isinstance(attr, tuple) else attr, getattr(form, attr[0] if isinstance(attr, tuple) else attr).data)

      transaction.tenant = dh.GetTenant(form.tenant.data)
      transaction.type = TransactionTypeDict[form.type.data]
      flash('Transaction information modified.', 'success')

    dh.Commit()
    return redirect('/billing/transactions')

  for field in form:
    for error in field.errors:
      flash('%s: %s' % (field.name, error), 'warning')

  return render_template('billing_transactions_edit.html', form = form, transaction = transaction)

@app.route('/billing/transactions/del/<int:transaction_id>')
def BillingTransactionsDelete(transaction_id):
  dh = get_session()
  dh.RemoveTransaction(transaction_id)
  flash('Transaction removed', 'success')
  dh.Commit()

  return redirect('/billing/transactions')

@app.route('/billing/bills', methods = ('GET', 'POST'))
def BillingBills():
  dh = get_session()

  bills = dh.GetAllBills()

  return render_template('billing_bills.html', bills = bills)

@app.route('/billing/bills/edit', defaults = {'bill_id': 0}, methods = ('GET', 'POST'))
@app.route('/billing/bills/edit/<int:bill_id>', methods = ('GET', 'POST'))
def BillingBillsEdit(bill_id):
  dh = get_session()
  form = FormEditBill()

  bill = None
  sorted_bill_entries = []
  if bill_id:
    bill = dh.GetBill(bill_id)

    form.end_date.data = bill.end_date
    form.begin_date.data = bill.begin_date
    form.recurring.data = bill.recurring

    if len(bill.entries):
      sorted_bill_entries.extend([e for e in bill.entries])
      sorted_bill_entries.sort(key = lambda a: a.tenant.name if a.tenant else 'zzzzzz')

  if form.validate_on_submit():
    if not bill:
      dh.AddBill(form.end_date.data, form.begin_date.data, recurring = float(form.recurring.data))

    return redirect('/billing/bills')

  for field in form:
    for error in field.errors:
      flash('%s: %s' % (field.name, error), 'warning')

  return render_template('billing_bills_edit.html', form = form, bill = bill, sorted_bill_entries = sorted_bill_entries)

@app.route('/billing/bills/del/<int:bill_id>')
def BillingBillsDelete(bill_id):
  dh = get_session()
  dh.RemoveBill(bill_id)
  flash('Transaction removed', 'success')
  dh.Commit()

  return redirect('/billing/bills')
