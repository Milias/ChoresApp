from common import *

@Singleton
class SQLDataHandler:
  def __init__(self, filename = 'config/data.db'):
    self.DataBaseFile = filename
    self.engine = None
    self.DBSession = None
    self.session = None

  """
    Database-related functions.
  """

  def Bind(self, filename):
    self.engine = create_engine('sqlite:///%s' % self.DataBaseFile)
    Base.metadata.bind = self.engine
    self.DBSession = sessionmaker(bind=self.engine)
    self.session = self.DBSession()

  def Create(self, filename):
    engine = create_engine('sqlite:///%s' % filename)
    Base.metadata.create_all(engine)

  def Commit(self):
    if self.session:
      self.session.commit()

  def Quit(self):
    self.session.commit()
    self.session.close()

  """
    Data manipulation.
  """

  def AddChore(self, name, description = '', value = 2.5):
    new_chore = Chore(name = name, description = description, value = value)
    self.session.add(new_chore)

  def RemoveChore(self, cid):
    self.session.remove(Chore).filter(Chore.id == cid)
