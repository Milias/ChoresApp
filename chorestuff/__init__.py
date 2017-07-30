import os
from flask import Flask

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
  DATABASE = os.path.join(app.root_path, 'chorestuff/config/data.db'),
  DEBUG = True,
  SECRET_KEY = 'secret',
))

app.config.from_envvar('CHORESTUFF_SETTINGS', silent=True)

from .common import *
from .sql import *
from .texport import *

csrf = CSRFProtect()
csrf.init_app(app)

parser = argparse.ArgumentParser(description='Chores tracker and bill generator.')

@app.route('/')
def index():
  tex = TeXporter.Instance()
  dh = DataHandler.Instance()
  dh.Bind('chorestuff/config/data.db')
  Base.metadata.drop_all(dh.engine)
  dh.Create('chorestuff/config/data.db')

  chores_dict = {}
  tenants = []

  assignments = [
    {
      'tenant': 'Francisco',
      'chore': 'Shower front',
      'is_manager': True,
      'is_home': True,
    },
    {
      'tenant': 'Hans',
      'chore': 'Shower back',
      'is_manager': False,
      'is_home': False,
    },
    {
      'tenant': 'Isaiah',
      'chore': 'Throw out glass',
      'is_manager': False,
      'is_home': True,
    },
    {
      'tenant': 'Jonatan',
      'chore': 'Clean cabinets & countertops',
      'is_manager': False,
      'is_home': True,
    },
    {
      'tenant': 'Luminița',
      'chore': 'Vacuum & mop hallway',
      'is_manager': False,
      'is_home': False,
    },
    {
      'tenant': 'Matthijs',
      'chore': 'Vacuum & mop kitchen',
      'is_manager': True,
      'is_home': True,
    },
    {
      'tenant': 'Nadiva',
      'chore': 'Throw out organic & plastic trash',
      'is_manager': False,
      'is_home': False,
    },
    {
      'tenant': 'Sjoerd',
      'chore': 'Clean stoves',
      'is_manager': False,
      'is_home': False,
    },
  ]

  bacc = dh.AddBankAccount(bank_name = 'ING', account = 'NL12INGB0001911092', holder = 'Studentenhuis Warande', location = 'Zeist')

  for assignment in assignments:
    new_tenant = dh.AddTenant(assignment['tenant'], is_manager = assignment['is_manager'], is_home = assignment['is_home'])
    new_chore = dh.AddChore(assignment['chore'])
    
    tenants.append(new_tenant)
    chores_dict[new_tenant.id] = new_chore

  extra_chores = [dh.AddChore('Toilet back'), dh.AddChore('Toilet front'), dh.AddChore('Throw out paper (wed-fri)')]

  bundle = dh.AddAssignmentBundle(date(2017, 7, 3), chores = chores_dict, extra_chores = extra_chores)
  bundle2 = dh.CycleBundle(bundle, repeat = 4)
  
  dh.AddExtraChores(bundle2[-1], extra_chores)

  with open('chorestuff/data/tex/chores_y%dw%d.tex' % bundle2[-1].date.isocalendar()[:2], 'w+') as f:
    f.write(tex.NewAssignmentsBundle(bundle2[-1]))

  return '<pre>%s</pre>' % (tex.NewAssignmentsBundle(bundle2[-1]))

  for a in bundle.assignments:
    if a.tenant:
      if not a.tenant.name == 'Francisco':
        dh.CompleteAssignment(a, tenant = a.tenant, date = date.today())

  bill = dh.AddBill(date.today(), recurring = 10.0)

  dh.AddTransaction(type = TransactionType.payment, tenant = tenants[1], date = date.today() + timedelta(days=3), amount = 12.5)
  dh.AddTransaction(type = TransactionType.expense, tenant = tenants[2], date = date.today() + timedelta(days=3), amount = 4.0)

  bill2 = dh.AddBill(date.today() + timedelta(days=15), recurring = 3.0)


"""
parser.add_argument('--db-file', '-db', action='store', type=str, default='videos.db', help='Path to DB file. (default: videos.db)')
parser.add_argument('--time-window', '-t', action='store', type=int, default=48, help='Time window to download subscriptions in hours. Zero means everything. (default: 48)')
parser.add_argument('--verbose', '-v', action='count', help='Verbosity of the output.')

parser.add_argument('files', action='store', nargs='*', type=str, default='', help='Links for standalone video download.')

parser.add_argument('--force', action='store_true', help='Force download of videos and metadata.')
parser.add_argument('--no-update-subscriptions', action='store_false', help='Do not update channel subscriptions.')
parser.add_argument('--no-extra-information', action='store_false', help='Do not download metadata.')
parser.add_argument('--no-download', action='store_false', help='Do not download pending videos.')
parser.add_argument('--no-update-videos', action='store_false', help='Do not check for newly uploaded videos.')
"""

