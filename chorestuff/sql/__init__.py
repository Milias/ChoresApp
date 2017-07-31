from .decl import *
from .access import *

def get_session():
  if not hasattr(g, 'dh'):
    g.dh = DataHandler.Instance()
    g.dh.Bind()
  return g.dh

@app.teardown_appcontext
def close_session(error):
  if hasattr(g, 'dh'):
    g.dh.Quit()

