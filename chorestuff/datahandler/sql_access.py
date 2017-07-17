from common import *

@Singleton
class SQLDataHandler:
  def __init__(self, filename = 'config/data.db'):
    self.DataBaseFile = filename

  def Bind(self, filename):
    self.engine = create_engine('sqlite:///%s' % self.DataBaseFile)
    Base.metadata.bind = self.engine
    self.DBSession = sessionmaker(bind=self.engine)
    self.session = self.DBSession()

  def Create(self, filename):
    engine = create_engine('sqlite:///%s' % filename)
    Base.metadata.create_all(engine)

  def Quit(self):
    self.session.commit()
    self.session.close()

