from ..common import *

@Singleton
class TeXporter:
  def __init__(self, export_path = 'tex/', template_path = 'chorestuff/tex/'):
    self.Path = export_path
    self.Templates = template_path

    self.Env = jinja2.Environment(
      block_start_string = '\BLOCK{',
      block_end_string = '}',
      variable_start_string = '\VAR{',
      variable_end_string = '}',
      comment_start_string = '\#{',
      comment_end_string = '}',
      line_statement_prefix = '%%',
      line_comment_prefix = '%#',
      trim_blocks = True,
      autoescape = False,
      loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )

  def NewAssignmentsBundle(self, bundle):
    template = self.Env.get_template('chorestuff/tex/chores-template.tex')
    return template.render(bundle = bundle, tex_escape = tex_escape, timedelta = timedelta, len = len, max = max)

  def NewBill(self, bill):
    template = self.Env.get_template('chorestuff/tex/bill-template.tex')

    sorted_bill_entries = [entry for entry in bill.entries]
    sorted_bill_entries.sort(key = lambda a: a.tenant.name if a.tenant else 'zzzzzz')
    return template.render(bill = bill, tex_escape = tex_escape, abs = abs, sorted_bill_entries = sorted_bill_entries)

  def NewBillDutch(self, bill):
    template = self.Env.get_template('chorestuff/tex/bill-template-dutch.tex')

    sorted_bill_entries = [entry for entry in bill.entries]
    sorted_bill_entries.sort(key = lambda a: a.tenant.name if a.tenant else 'zzzzzz')
    return template.render(bill = bill, tex_escape = tex_escape, abs = abs, sorted_bill_entries = sorted_bill_entries)

  def NewExpensesTable(self, begin_date, end_date):
    template = self.Env.get_template('chorestuff/tex/expenses-table.tex')
    return template.render(begin_date = begin_date, end_date = end_date, tex_escape = tex_escape)

def get_texporter():
  if not hasattr(g, 'tex'):
    g.tex = TeXporter.Instance()
  return g.tex

