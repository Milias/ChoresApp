from ..common import *
from .decl import *

@Singleton
class DataHandler:
  def __init__(self):
    self.session = None

  """
    Database-related functions.
  """

  def Bind(self, filename):
    self.engine = create_engine('sqlite:///%s' % filename)
    Base.metadata.bind = self.engine
    self.DBSession = sessionmaker(bind=self.engine)
    self.session = self.DBSession()

  def Create(self, filename):
    engine = create_engine('sqlite:///%s' % filename)
    Base.metadata.create_all(engine)

    self.Bind(filename)

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

  def AddChore(self, name):
    chore = self.session.query(Chore).filter(Chore.name == name).first()

    if chore: return chore

    new_chore = Chore(name = name)
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
      print('Error getting chore: id not found.')

    return chore

  """
    Tenant manipulation
  """

  def AddTenant(self, name):
    tenant = self.session.query(Tenant).filter(Tenant.name == name).first()

    if tenant: return tenant

    new_tenant = Tenant(name = name)
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
      print('Error getting tenant: id not found.')

    return tenant

  """
    Assignments manipulation
  """

  def AddAssignmentBundle(self, date, init = True):
    # Convert date object to calendar week (integer).
    week = date.isocalendar()[1]

    bundle = self.session.query(AssignmentBundle).filter(AssignmentBundle.week == week).first()

    if bundle: return bundle

    new_bundle = AssignmentBundle(week = week)

    if init:
      self.InitAssignmentBundle(new_bundle)

    self.session.add(new_bundle)

    return new_bundle

  def InitAssignmentBundle(self, new_bundle):
    for tenant in self.GetLivingTenants():
      new_assignment = Assignment(tenant = tenant, bundle = new_bundle, is_tenant_home = tenant.is_home)
      self.session.add(new_assignment)

  def GetAllAssignmentBundles(self, sorted = False):
    if sorted:
      return self.session.query(AssignmentBundle).order_by(AssignmentBundle.week.asc()).all()

    return self.session.query(AssignmentBundle).all()

  def GetAssignmentBundle(self, id):
    bundle = self.session.query(AssignmentBundle).filter(AssignmentBundle.id == id).first()

    if bundle == None:
      print('Error getting assignment bundle: id not found.')

    return bundle

  def GetAssignmentBundleByWeek(self, week):
    bundle = self.session.query(AssignmentBundle).filter(AssignmentBundle.week == week).first()

    if bundle == None:
      print('Error getting assignment bundle: week not found.')

    return bundle
