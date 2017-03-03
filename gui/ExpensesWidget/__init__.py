# -*- coding: utf8 -*-
import functools

from datahandler import *
from .TransactionWidget import *
from .PersonalBillsWidget import *
from .GroupBillsWidget import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

"""
  Expenses and Payments - Tab Widget
"""

class ExpPayWidget(QWidget):
  def __init__(self, name, parent, dho):
    super().__init__(parent.TabBox)
    self.DataHandlerObject = dho

    self.Grid = QGridLayout(self)

    self.Parent = parent
    self.Name = name

    self.Init()
    self.TabOrdering = { 0 : 'Expenses', 1 : 'Payments', 2 : 'Bills' }
    self.TabWidgetTypes = { 'Expenses' : TabExpensesWidget, 'Payments' : TabPaymentsWidget, 'Bills' : TabBillsWidget }

    for i in range(len(self.TabOrdering)): self.InitTab(i)

  def Init(self):
    self.TabWidgets = {}

    self.TabBox = QTabWidget(self)
    self.Grid.addWidget(self.TabBox, 0, 0)

    self.DateWidget = QWidget(self)
    self.DateBox = QHBoxLayout(self.DateWidget)
    self.Grid.addWidget(self.DateWidget, 1, 0, 1, 3, Qt.AlignHCenter)

    self.DateBox.addWidget(QLabel('Choose date interval:', self.DateWidget), 0, Qt.AlignLeft)

    self.DateInterval = [QDateEdit(QDate(datetime.date.today() - datetime.timedelta(days=60)), self.DateWidget), QDateEdit(QDate(datetime.date.today()), self.DateWidget)]

    for i, DE in enumerate(self.DateInterval):
      DE.setDisplayFormat('yyyy-MM-dd')
      self.DateBox.addWidget(DE, i + 1, Qt.AlignHCenter)

    bupdate = QPushButton('Update', self)
    bupdate.clicked.connect(self.LoadTransactions)
    self.DateBox.addWidget(bupdate, len(self.DateInterval) + 1)

  def InitTab(self, index):
    name = self.TabOrdering[index]
    self.TabWidgets[name] = self.TabWidgetTypes[name](name, self, self.DataHandlerObject)
    self.TabBox.addTab(self.TabWidgets[name], name)

  def LoadTransactions(self):
    py_dates = [qd.date().toPyDate() for qd in self.DateInterval]
    self.TabBox.currentWidget().TransWidget.LoadTransactions(*py_dates)

"""
  Expenses - Tab Widget
"""

class TabExpensesWidget(QWidget):
  def __init__(self, name, parent, dho):
    super().__init__(parent.TabBox)
    self.DataHandlerObject = dho

    self.Grid = QGridLayout(self)
    self.Grid.setSpacing(10)

    self.Parent = parent
    self.Name = name

    self.TransWidget = TransactionsWidget(self.DataHandlerObject, 'expenses', self)

    self.TransScroll = QScrollArea(self)
    self.TransScroll.setWidget(self.TransWidget)
    self.TransScroll.setAlignment(Qt.AlignHCenter)
    self.Grid.addWidget(self.TransScroll, 0, 0)

"""
  Payments - Tab Widget
"""

class TabPaymentsWidget(QWidget):
  def __init__(self, name, parent, dho):
    super().__init__(parent.TabBox)
    self.DataHandlerObject = dho

    self.Grid = QGridLayout(self)
    self.Grid.setSpacing(10)

    self.Parent = parent
    self.Name = name

    self.TransWidget = TransactionsWidget(self.DataHandlerObject, 'payments', self)

    self.TransScroll = QScrollArea(self)
    self.TransScroll.setWidget(self.TransWidget)
    self.TransScroll.setAlignment(Qt.AlignHCenter)
    self.Grid.addWidget(self.TransScroll, 0, 0)

"""
  Bills - Tab Widget
"""

class TabBillsWidget(QWidget):
  def __init__(self, name, parent, dho):
    super().__init__(parent.TabBox)
    self.DataHandlerObject = dho

    self.Grid = QGridLayout(self)
    self.Grid.setSpacing(10)

    self.Parent = parent
    self.Name = name

    self.TransWidget = GroupBillsWidget(self.DataHandlerObject, self)

    self.GBillsScroll = QScrollArea(self)
    self.GBillsScroll.setWidget(self.TransWidget)
    self.GBillsScroll.setAlignment(Qt.AlignHCenter)
    self.GBillsScroll.setFixedWidth(450)
    self.Grid.addWidget(self.GBillsScroll, 0, 0)

    self.PBillsWidget = PersonalBillsWidget(self.DataHandlerObject, self)

    self.PBillsScroll = QScrollArea(self)
    self.PBillsScroll.setWidget(self.PBillsWidget)
    self.PBillsScroll.setAlignment(Qt.AlignHCenter)
    self.PBillsScroll.setFixedWidth(800)
    self.Grid.addWidget(self.PBillsScroll, 0, 1)

  def ConnectSignal(self, widget):
    widget.ShowPersonalBillsSignal.connect(lambda: self.PBillsWidget.LoadTransactions(widget.buuid))
