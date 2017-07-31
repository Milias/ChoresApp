from ..common import *
from ..sql import *

class FormEditTenant(RedirectForm):
  id = HiddenField('Id:')
  name = StringField('Name: ', validators=[InputRequired(), Length(max=256)])
  email = EmailField('Email address: ', validators=[InputRequired(), Email(), Length(max=256)])

  is_living = BooleanField('Living: ', default=True)
  is_home = BooleanField('Home: ', default=True)
  is_manager = BooleanField('Manager: ', default=False)

class FormEditChore(RedirectForm):
  id = HiddenField('Id:')
  name = StringField('Name: ', validators=[InputRequired(), Length(max=256)])
  value = DecimalField('Value: ', validators=[InputRequired()])
  description = TextAreaField('Description:', validators=[Optional()])

@app.route('/house/tenants')
def HouseTenants():
  dh = get_session()
  tenants = dh.GetAllTenants(sorted = True)
  return render_template('house_tenants.html', dh = dh, tenants = tenants)

@app.route('/house/tenants/edit', defaults = {'tenant_id': 0}, methods = ('GET', 'POST'))
@app.route('/house/tenants/edit/<int:tenant_id>', methods = ('GET', 'POST'))
def HouseTenantsEdit(tenant_id):
  dh = get_session()
  form = FormEditTenant()

  tenant = None
  if tenant_id:
    tenant = dh.GetTenant(tenant_id)
    if tenant:
      for attr in ('id', 'name', 'email', 'is_living', 'is_home', 'is_manager'):
        setattr(getattr(form, attr), 'data', getattr(tenant, attr))

  if form.validate_on_submit():
    tenant = dh.GetTenant(form.id.data)
    if tenant == None:
      tenant = dh.AddTenant(name = form.name.data, email = form.email.data, is_living = form.is_living.data, is_home = form.is_home.data, is_manager = form.is_manager.data)
      flash('Tenant added.', 'success')
    else:
      for attr in ('name', 'email', 'is_living', 'is_home', 'is_manager'):
        setattr(tenant, attr, getattr(form, attr).data)
      flash('Tenant information modified.', 'success')

    dh.Commit()
    return redirect('/house/tenants')

  for field in form:
    for error in field.errors:
      flash('%s: %s' % (field.name, error), 'warning')

  return render_template('house_tenants_edit.html', dh = dh, tenant = tenant, form = form)

@app.route('/house/tenants/del/<int:tenant_id>')
def HouseTenantsDelete(tenant_id):
  dh = get_session()
  dh.RemoveTenant(tenant_id)
  flash('Removed %d.' % tenant_id, 'success')
  dh.Commit()

  return redirect('/house/tenants')

@app.route('/house/chores')
def HouseChores():
  dh = get_session()
  chores = dh.GetAllChores()
  return render_template('house_chores.html', dh = dh, chores = chores)

@app.route('/house/chores/edit', defaults = {'chore_id': 0}, methods = ('GET', 'POST'))
@app.route('/house/chores/edit/<int:chore_id>', methods = ('GET', 'POST'))
def HouseChoresEdit(chore_id):
  dh = get_session()
  form = FormEditChore()

  chore = None
  if chore_id:
    chore = dh.GetChore(chore_id)
    if chore:
      for attr in ('id', 'name', 'value', 'description'):
        setattr(getattr(form, attr), 'data', getattr(chore, attr))

  if form.validate_on_submit():
    chore = dh.GetChore(form.id.data)
    if chore == None:
      chore = dh.AddChore(form.name.data, value = form.value.data)
      flash('Chore added.', 'success')
    else:
      for attr in ('name', 'value', 'description'):
        setattr(chore, attr, getattr(form, attr).data)
      flash('Chore information modified.', 'success')

    dh.Commit()
    return redirect('/house/chores')

  for field in form:
    for error in field.errors:
      flash('%s: %s' % (field.name, error), 'warning')

  return render_template('house_chores_edit.html', dh = dh, chore = chore, form = form)

