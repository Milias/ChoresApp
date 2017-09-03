from ..common import *
from ..sql import *
from ..texport import *

class FormEditTenant(RedirectForm):
  tenant_id = HiddenField('Id:')
  name = StringField('Name: ', validators=[InputRequired(), Length(max=256)])
  email = EmailField('Email address: ', validators=[InputRequired(), Email(), Length(max=256)])

  is_living = BooleanField('Living: ', default=True)
  is_home = BooleanField('Home: ', default=True)
  is_manager = BooleanField('Manager: ', default=False)

class FormEditChore(RedirectForm):
  chore_id = HiddenField('Id:')
  name = StringField('Name: ', validators=[InputRequired(), Length(max=256)])
  value = DecimalField('Value: ', validators=[InputRequired()])
  description = TextAreaField('Description:', validators=[Optional()])

class FormEditAssignment(RedirectForm):
  assignment_id = HiddenField('Id:')
  bundle_id = HiddenField('Bundle Id:')

  is_tenant_home = SelectField('Is home:', choices = [(-1, ''), (1, 'Yes'), (0, 'No')], coerce=int, validators=[InputRequired()])
  tenant = SelectField('Tenant:', choices = [], coerce=int, validators=[Optional()])
  chore = SelectField('Chore:', choices = [], coerce=int, validators=[Optional()])
  completed = SelectMultipleField('Completed by:', choices = [], coerce=int, validators=[Optional()])
  date = DateField('Completion date:', validators = [Optional()])

class FormEditAssignmentBundle(RedirectForm):
  bundle_id = HiddenField('Id:')
  date = DateField('Assignment date:', default = lambda: date.today() - timedelta(days=date.today().isocalendar()[2] - 1), validators = [InputRequired()])

  assignments = FieldList(FormField(FormEditAssignment))

"""
  Tenants
"""

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
      for attr in (('tenant_id', 'id'), 'name', 'email', 'is_living', 'is_home', 'is_manager'):
        setattr(getattr(form, attr[0] if type(attr)==type((1,)) else attr), 'data', getattr(tenant, attr[1] if type(attr)==type((1,)) else attr))

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

"""
  Chores
"""

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
      for attr in (('chore_id', 'id'), 'name', 'value', 'description'):
        setattr(getattr(form, attr[0] if type(attr)==type((1,)) else attr), 'data', getattr(chore, attr[1] if type(attr)==type((1,)) else attr))

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

@app.route('/house/chores/del/<int:chore_id>')
def HouseChoresDelete(chore_id):
  dh = get_session()
  dh.RemoveChore(chore_id)
  flash('Removed %d.' % chore_id, 'success')
  dh.Commit()

  return redirect('/house/chores')

"""
  Assignment Bundles
"""

@app.route('/house/bundles', defaults = {'bundle_id': 0})
@app.route('/house/bundles/<int:bundle_id>', methods = ('GET', 'POST'))
def HouseBundles(bundle_id):
  dh = get_session()
  tex = get_texporter()
  bundles = dh.GetAllAssignmentBundles(sorted = True)

  chosen_bundle = None
  tex_str = None
  if bundle_id:
    chosen_bundle = dh.GetAssignmentBundle(bundle_id)

  if chosen_bundle:
    # Sort assignments by tenants' names and put (anyone) at the end.
    chosen_bundle.assignments.sort(key = lambda a: a.tenant.name if a.tenant else 'zzzzzz')

    tex_str = tex.NewAssignmentsBundle(chosen_bundle)

  return render_template('house_bundles.html', dh = dh, bundles = bundles, chosen_bundle = chosen_bundle, tex_str = tex_str)

@app.route('/house/bundles/copy/<int:bundle_id>', methods = ('GET', 'POST'))
def HouseBundlesCopy(bundle_id):
  dh = get_session()

  bundle = dh.GetAssignmentBundle(bundle_id)

  if bundle == None:
    return redirect('/house/bundles/edit')

  else:
    bundle = dh.CycleBundle(bundle, 1)[-1]
    dh.Commit()

    flash('Assignment copied and cycled', 'success')

  return redirect('/house/bundles/%d' % bundle.id)

@app.route('/house/bundles/edit', defaults = {'bundle_id': 0}, methods = ('GET', 'POST'))
@app.route('/house/bundles/edit/<int:bundle_id>', methods = ('GET', 'POST'))
def HouseBundlesEdit(bundle_id):
  dh = get_session()
  form = FormEditAssignmentBundle()

  living_tenants = dh.GetLivingTenants(sorted = True)
  tenants_choices = [(0, '(anyone)')] + [(tenant.id, tenant.name) for tenant in living_tenants]
  tenants_comp_choices = [(0, '')] + [(tenant.id, tenant.name) for tenant in living_tenants]

  chores = dh.GetAllChores()
  chores_choices = [(0, '')] + [(chore.id, '%s' % (chore.name)) for chore in chores]

  bundle = None
  if bundle_id:
    bundle = dh.GetAssignmentBundle(bundle_id)

  if bundle:
    form.date.data = bundle.date
    # Sort assignments by tenants' names and put (anyone) at the end.
    bundle.assignments.sort(key = lambda a: a.tenant.name if a.tenant else 'zzzzzz')
    if len(form.assignments.entries) == 0:
      form.bundle_id.data = bundle.id

      for assignment in bundle.assignments:
        entry = form.assignments.append_entry()
        entry.tenant.choices = tenants_choices
        entry.chore.choices = chores_choices
        entry.completed.choices = tenants_comp_choices[1:]

        entry.tenant.data = assignment.tenant.id if assignment.tenant else 0
        entry.is_tenant_home.data = assignment.is_tenant_home if assignment.tenant else -1
        entry.chore.data = assignment.chore.id if assignment.chore else 0
        entry.completed.data = [ completion.tenant.id for completion in assignment.completions if completion.tenant ]
        print(entry.completed.data)
        entry.assignment_id.data = assignment.id
        entry.bundle_id.data = bundle.id

      for i in range(3):
        entry = form.assignments.append_entry()
        entry.tenant.data = 0
        entry.is_tenant_home.data = -1
        entry.chore.data = 0

        entry.assignment_id.data = 0
        entry.bundle_id.data = 0

        entry.tenant.choices = tenants_choices
        entry.chore.choices = chores_choices
        entry.completed.choices = tenants_comp_choices

    for entry in form.assignments.entries:
      entry.tenant.choices = tenants_choices
      entry.chore.choices = chores_choices
      entry.completed.choices = tenants_comp_choices

  else:
    # Creates assignments only if there are none.
    if len(form.assignments.entries) == 0:
      form.date.data = dh.GetBundleDate(date.today())
      form.bundle_id.data = 0

      for tenant in living_tenants:
        entry = form.assignments.append_entry()
      for i in range(3):
        entry = form.assignments.append_entry()

      for entry, tenant in zip(form.assignments.entries, living_tenants + 3*[None]):
        entry.tenant.data = tenant.id if tenant else 0
        entry.is_tenant_home.data = tenant.is_home if tenant else -1
        entry.chore.data = 0

        entry.assignment_id.data = 0
        entry.bundle_id.data = 0

    for entry in form.assignments.entries:
      entry.tenant.choices = tenants_choices
      entry.chore.choices = chores_choices
      entry.completed.choices = tenants_comp_choices

  if form.validate_on_submit():
    chores_dict = {}
    home_dict = {}
    extra_chores = []
    completed_chores = {}

    for assignment in form.assignments.entries:
      if assignment.tenant.data:
        # Assignment for a tenant.
        chores_dict[assignment.tenant.data] = dh.GetChore(assignment.chore.data)
        home_dict[assignment.tenant.data] = assignment.is_tenant_home.data > 0

      elif assignment.chore.data:
        # Assignment for anyone.
        extra_chores.append(dh.GetChore(assignment.chore.data))

      if assignment.completed.data:
        completed_chores[assignment.assignment_id.data] = assignment.completed.data

    bundle = dh.GetAssignmentBundle(form.bundle_id.data)
    if bundle == None:
      bundle = dh.AddAssignmentBundle(form.date.data, chores = chores_dict, extra_chores = extra_chores)

      flash('Assignment created.', 'success')
    else:
      bundle.date = dh.GetBundleDate(form.date.data)
      if chores_dict:
        dh.SetAssignmentsChores(bundle, chores_dict)

      if extra_chores:
        dh.AddExtraChores(bundle, extra_chores)

      if home_dict:
        dh.SetTenantIsHome(bundle, home_dict)

      flash('Assignment modified.', 'success')

    for assignment_id in completed_chores:
      assignment = dh.GetAssignment(assignment_id)
      if assignment:
        dh.CompleteAssignment(assignment, completed_chores[assignment_id])

    dh.Commit()
    return redirect('/house/bundles/%d' % bundle.id)

  for field in form:
    for error in field.errors:
      flash('%s: %s' % (field.name, error), 'warning')

  return render_template('house_bundles_edit.html', dh = dh, bundle = bundle, form = form)

@app.route('/house/bundles/del/<int:bundle_id>')
def HouseBundlesDelete(bundle_id):
  dh = get_session()
  dh.RemoveAssignmentBundle(bundle_id)
  flash('Assignment removed', 'success')
  dh.Commit()

  return redirect('/house/bundles')

@app.route('/house/assignments/del/<int:assignment_id>/<int:bundle_id>')
def HouseAssignmentsDelete(assignment_id, bundle_id):
  dh = get_session()
  dh.RemoveAssignment(assignment_id)
  flash('Assignment entry removed', 'success')
  dh.Commit()

  return redirect('/house/bundles/edit/%d' % bundle_id)

