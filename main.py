from chorestuff import *

dh = DataHandler.Instance()
dh.Create('chorestuff/config/data.db')

for name in ['Francisco', 'Luminita', 'Matthijs', 'Jonatan']:
  dh.AddTenant(name)

for name in ['Sweep hallway', 'Garbage']:
  dh.AddChore(name)

for tenant in dh.GetAllTenants(sorted=True):
  print(tenant.name)

for chore in dh.GetAllChores():
  print(chore.name)

bundle = dh.AddAssignmentBundle(date.today())

print(bundle.week)

dh.Quit()
