from common import *

@app.route('/')
def Index():
  return render_template('index.html')

