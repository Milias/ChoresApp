from chorestuff import *

tex = TeXporter.Instance()

dh = DataHandler.Instance()
dh.Bind('chorestuff/config/data.db')
Base.metadata.drop_all(dh.engine)
dh.Create('chorestuff/config/data.db')

tenant_names = ['Francisco', 'Luminita', 'Matthijs', 'Jonatan']
chores_names = ['Sweep hallway', 'Garbage', 'Clean filter', 'Do stuff']
chores_dict = {}
tenants = []

bacc = dh.AddBankAccount(bank_name = 'ING', account = 'NL12INGB0001911092', holder = 'Studentenhuis Warande', location = 'Zeist')

for t_name, c_name in zip(tenant_names, chores_names):
  tenants.append(dh.AddTenant(t_name))

  if t_name == 'Francisco' or t_name == 'Matthijs':
    tenants[-1].is_manager = True

  if t_name == 'Luminita':
    tenants[-1].is_home = False

  chore = dh.AddChore(c_name)

  chores_dict[tenants[-1].id] = chore

del chores_dict[tenants[-1].id]

extra_chores = [dh.AddChore('Paper'), dh.AddChore('Fridge')]

bundle = dh.AddAssignmentBundle(date.today(), chores = chores_dict, extra_chores = extra_chores)

for a in bundle.assignments:
  if a.tenant:
    if not a.tenant.name == 'Francisco':
      dh.CompleteAssignment(a, tenant = a.tenant, date = date.today())

#print(tex.NewAssignmentsBundle(bundle))

bill = dh.AddBill(date.today(), recurring = 10.0)

print(tex.NewBill(bill))

dh.AddTransaction(type = TransactionType.payment, tenant = tenants[1], date = date.today() + timedelta(days=3), amount = 12.5)
dh.AddTransaction(type = TransactionType.expense, tenant = tenants[2], date = date.today() + timedelta(days=3), amount = 4.0)

bill2 = dh.AddBill(date.today() + timedelta(days=15), recurring = 3.0)

print(tex.NewBill(bill2))

