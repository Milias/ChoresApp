from chorestuff import *

dh = DataHandler.Instance()
dh.Create('chorestuff/config/data.db')
Base.metadata.drop_all(dh.engine)
dh.Create('chorestuff/config/data.db')

for name in ['Francisco', 'Luminita', 'Matthijs', 'Jonatan']:
  tenant = dh.AddTenant(name)

for name in ['Sweep hallway', 'Garbage']:
  dh.AddChore(name)

for tenant in dh.GetAllTenants(sorted=True):
  print(tenant.name)

for chore in dh.GetAllChores():
  print(chore.name)

bundle = dh.AddAssignmentBundle(date.today())

for a in bundle.assignments:
  if a.tenant:
    print('tenant')

  if a.chore:
    print('chore')

dh.Quit()
