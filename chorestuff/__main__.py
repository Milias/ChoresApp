import os
from flask import Flask

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
  DATABASE = os.path.join(app.root_path, 'config/data.db'),
  DEBUG = True,
  SECRET_KEY = 'secret',
))

app.config.from_envvar('CHORESTUFF_SETTINGS', silent=True)

from common import *
from sql import *
from texport import *
from pages import *

csrf = CSRFProtect()
csrf.init_app(app)

parser = argparse.ArgumentParser(description='Chores tracker and bill generator.')

if __name__ == '__main__':
  app.run(debug = True, host = '0.0.0.0')
