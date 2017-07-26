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
    return template.render(bundle = bundle, timedelta=timedelta, len=len, max=max)

  def NewBill(self, bill):
    template = self.Env.get_template('chorestuff/tex/bill-template.tex')
    return template.render(bill = bill, abs = abs)
