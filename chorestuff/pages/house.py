from ..common import *
from ..sql import *

@app.route('/house/tenants')
def HouseTenants():
  dh = get_session()
  tenants = dh.GetLivingTenants(sorted = True)
  return render_template('house_tenants.html', dh = dh, tenants = tenants)
