from chorestuff import *

dh = DataHandler.Instance()
dh.Bind('chorestuff/config/data.db')
Base.metadata.drop_all(dh.engine)
dh.Create('chorestuff/config/data.db')

tenant_names = ['Francisco', 'Luminita', 'Matthijs', 'Jonatan']
chores_names = ['Sweep hallway', 'Garbage', 'Clean filter', 'Do stuff']
chores_dict = {}

for t_name, c_name in zip(tenant_names, chores_names):
  tenant = dh.AddTenant(t_name)

  if t_name == 'Francisco' or t_name == 'Matthijs':
    tenant.is_manager = True

  chore = dh.AddChore(c_name)

  chores_dict[tenant.id] = chore

bundle = dh.AddAssignmentBundle(date.today(), chores = chores_dict)

for a in bundle.assignments:
  if not a.tenant.name == 'Francisco':
    dh.CompleteAssignment(a, tenant = a.tenant, date = date.today())

bill = dh.AddBill(date.today(), recurring = 10.0)

dh.AddTransaction(type = TransactionType.payment, tenant = tenant, date = date.today() + timedelta(days=3), amount = 12.5)

bill2 = dh.AddBill(date.today() + timedelta(days=15), recurring = 12.0)

print('First')
print('%s to %s' % (bill.begin_date, bill.end_date))
for entry in bill.entries:
  print(entry)

print('\nSecond')
print('%s to %s' % (bill2.begin_date, bill2.end_date))
for entry in bill2.entries:
  print(entry)

dh.Quit()
