from ..common import *
from ..sql import *
from ..texport import *

class FormEditTransaction(RedirectForm):
  transaction_id = HiddenField('Id:')
  type = SelectField('Type:', default = 1, choices = [(1, 'Expense'), (2, 'Payment'), (4, 'Bill'), (8, 'Other')], coerce=int, validators=[InputRequired()])
  tenant = SelectField('Tenant:', choices = [], coerce=int, validators=[Optional()])
  description = TextAreaField('Description:', validators=[Optional()])
  date = DateField('Date:', default = lambda: date.today() - timedelta(days=date.today().isocalendar()[2] - 1), validators = [InputRequired()])
  amount = DecimalField('Amount:', validators=[InputRequired()])

@app.route('/billing/transactions')
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

  living_tenants = dh.GetLivingTenants(sorted = True)
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
