# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

"""
  Group bills item widget
"""

class GroupBillsItemWidget(QFrame):
  ShowPersonalBillsSignal = pyqtSignal(str)

  def __init__(self, dho, buuid, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QGridLayout(self)

    self.buuid = buuid
    self.tkey = 'group_bills'

    self.setFixedSize(425, 90)
    self.setFrameStyle(QFrame.Plain | QFrame.StyledPanel)

    self.Grid.addWidget(QLabel('<b>Issued</b>', self), 0, 0, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Range</b>', self), 1, 0, Qt.AlignRight)

    self.Grid.addWidget(QLabel('<b>Shopping</b>', self), 0, 2, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Recurring</b>', self), 1, 2, Qt.AlignRight)

    self.Inputs = {
      'date' : [
        QLabel('', self), (0, 1, Qt.AlignLeft)
      ],

      'date_range' : [
        QLabel('', self), (1, 1, Qt.AlignLeft)
      ],

      'shared_shopping_costs' : [
        QLabel('0.00€', self), (0, 3, Qt.AlignLeft)
      ],

      'recurring' : [
        QLabel('0.00€', self), (1, 3, Qt.AlignLeft)
      ],

      'view' : [
        QPushButton('', self), (0, 4, Qt.AlignRight),
        lambda q: (
          q.setIcon(QIcon('gui/icons/view.svg')),
          q.setIconSize(QSize(32, 32)),
          q.setFixedSize(32, 32),
          q.clicked.connect(self.EmitViewSignal)
        )
      ],

      'tex' : [
        QPushButton('', self), (0, 5, Qt.AlignRight),
        lambda q: (
          q.setIcon(QIcon('gui/icons/tex.svg')),
          q.setIconSize(QSize(28, 28)),
          q.setFixedSize(32, 32),
          q.clicked.connect(self.SaveToTex)
        )
      ],

      'delete' : [
        QPushButton('', self), (1, 4, Qt.AlignRight),
        lambda q: (
          q.setIcon(QIcon('gui/icons/delete.svg')),
          q.setIconSize(QSize(32, 32)),
          q.setFixedSize(32, 32),
          q.clicked.connect(self.Delete)
        )
      ]
    }

    for key in self.Inputs:
      if len(self.Inputs[key]) > 2:
        self.Inputs[key][2](self.Inputs[key][0])
      self.Grid.addWidget(self.Inputs[key][0], *self.Inputs[key][1])

    self.Update()

  def Update(self):
    if self.buuid is None: return

    self.BillData = self.DataHandlerObject.BillingData[self.tkey][self.buuid]['group_bill_data']

    self.Inputs['date'][0].setText('%s' % datetime.date(*self.DataHandlerObject.BillingData[self.tkey][self.buuid]['date']))

    date_range = tuple([datetime.datetime.strftime(datetime.date(*d), '%m-%d') for d in self.DataHandlerObject.BillingData[self.tkey][self.buuid]['date_range']])
    self.Inputs['date_range'][0].setText('%s/%s' % date_range)

    for key in self.BillData:
      if key in self.Inputs:
        self.Inputs[key][0].setText(u'%.2f€' % self.BillData[key])

  def SetUUID(self, new_buuid):
    self.buuid = new_buuid
    self.Update()

  def Delete(self):
    self.hide()

    for uuid in self.DataHandlerObject.BillingData[self.tkey][self.buuid]['buuids']:
      self.DataHandlerObject.BillingRemoveItem('bills', uuid)

    self.DataHandlerObject.BillingRemoveItem('group_bills', self.buuid)
    self.buuid = None

  def EmitViewSignal(self):
    self.ShowPersonalBillsSignal.emit(self.buuid)

  def SaveToTex(self):
    self.DataHandlerObject.BillingSaveToTex(self.buuid)

"""
  Group bills widget
"""

class GroupBillsWidget(QWidget):
  def __init__(self, dho, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.CastedParent = parent

    self.Grid = QVBoxLayout(self)
    self.Grid.setAlignment(Qt.AlignHCenter)
    self.Grid.setSizeConstraint(QLayout.SetMinAndMaxSize)

    self.tkey = 'group_bills'

    self.TransactionItems = []

  def LoadTransactions(self, py_date0, py_date1):
    for widget in self.TransactionItems:
      widget.hide()

    for i, uuid in enumerate(self.DataHandlerObject.BillingGetItemsInRange(self.tkey, py_date0, py_date1)):
      if i < len(self.TransactionItems):
        self.TransactionItems[i].SetUUID(uuid)
        self.TransactionItems[i].show()
      else:
        self.NewTransaction(uuid)

  def NewTransaction(self, buuid):
    self.TransactionItems.append(GroupBillsItemWidget(self.DataHandlerObject, buuid, self))
    self.CastedParent.ConnectSignal(self.TransactionItems[-1])
    self.Grid.addWidget(self.TransactionItems[-1], len(self.TransactionItems), Qt.AlignHCenter)
