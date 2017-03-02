# -*- coding: utf8 -*-
from .ChoresWidget import *
from .ParticipantsWidget import *
from .AssignWidget import *
from .BillingWidget import *
from .ExpensesWidget import *

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.DataHandlerObject = DataHandler()
    self.setCentralWidget(QWidget())
    self.Init()

    self.TabOrdering = { 0 : 'Assignments', 1 : 'Chores', 2 : 'Participants', 3 : 'Expenses, Payments && Bills', 4 : 'Billing' }
    self.TabWidgetTypes = { 'Chores' : ChoresWidget, 'Participants' : ParticipantsWidget, 'Assignments' : AssignmentsWidget, 'Billing' : BillingWidget, 'Expenses, Payments && Bills' : ExpPayWidget }
    self.UpdateFunctions = { 'Assignments' : lambda w: w.Update() }

    for i in range(len(self.TabOrdering)): self.InitTab(i)

    self.resize(1024,768)
    self.center()
    self.setWindowTitle('ChoresApp')
    self.show()

  def Init(self):
    self.TabWidgets = {}

    grid = QGridLayout()
    self.centralWidget().setLayout(grid)

    self.TabBox = QTabWidget(self)
    self.TabBox.currentChanged[int].connect(self.UpdateTab)
    grid.addWidget(self.TabBox, 0, 0)

  def InitTab(self, index):
    name = self.TabOrdering[index]
    self.TabWidgets[name] = self.TabWidgetTypes[name](name, self, self.DataHandlerObject)
    self.TabBox.addTab(self.TabWidgets[name], name)

  def UpdateTab(self, index):
    name = self.TabOrdering[index]
    if name in self.UpdateFunctions:
      self.UpdateFunctions[name](self.TabWidgets[name])

  def center(self):
    qr = self.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())
