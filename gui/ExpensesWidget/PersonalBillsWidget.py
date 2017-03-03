# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

"""
  Personal bills item widget
"""

class PersonalBillsItemWidget(QFrame):
  def __init__(self, dho, buuid, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QGridLayout(self)

    self.buuid = buuid
    self.tkey = 'bills'

    self.setFixedSize(700, 90)
    self.setFrameStyle(QFrame.Plain | QFrame.StyledPanel)

    self.Grid.addWidget(QLabel('<b>Name</b>', self), 0, 0, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Shopping</b>', self), 1, 0, Qt.AlignRight)

    self.Grid.addWidget(QLabel('<b>Contribution</b>', self), 0, 2, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Chores</b>', self), 1, 2, Qt.AlignRight)

    self.Grid.addWidget(QLabel('<b>Subtotal</b>', self), 1, 4, Qt.AlignHCenter)

    #'%Y-%m-%d %H:%M:%S.%f')

    self.Inputs = {
      'name' : [
        QLabel('', self), (0, 1, Qt.AlignLeft)
      ],

      'personal_shopping_costs' : [
        QLabel('0.00€', self), (1, 1, Qt.AlignLeft)
      ],

      'contribution' : [
        QLabel('0.00€', self), (0, 3, Qt.AlignLeft)
      ],

      'chores' : [
        QLabel('0.00€', self), (1, 3, Qt.AlignLeft)
      ],

      'subtotal' : [
        QLabel('0.00€', self), (0, 4, Qt.AlignHCenter),
        lambda q: (
          q.setFont(QFont('Arial', 24, 0)),
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

    self.BillData = self.DataHandlerObject.BillingData[self.tkey][self.buuid]['bill_data']

    self.Inputs['name'][0].setText(self.DataHandlerObject.GetItemKey('participants', self.DataHandlerObject.BillingData[self.tkey][self.buuid]['puuid'], 'name'))

    for key in self.BillData:
      if key in self.Inputs:
        self.Inputs[key][0].setText(u'%.2f€' % self.BillData[key])

  def SetUUID(self, new_buuid):
    self.buuid = new_buuid
    self.Update()

"""
  Personal bills widget
"""

class PersonalBillsWidget(QWidget):
  def __init__(self, dho, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QVBoxLayout(self)
    self.Grid.setAlignment(Qt.AlignHCenter)

    self.Grid.setSizeConstraint(QLayout.SetMinAndMaxSize)

    self.tkey = 'bills'

    self.TransactionItems = []

  def LoadTransactions(self, gbuuid):
    for widget in self.TransactionItems:
      widget.hide()

    relevant_buuids = self.DataHandlerObject.BillingData['group_bills'][gbuuid]['buuids']

    for i, buuid in enumerate(relevant_buuids):
      if i < len(self.TransactionItems):
        self.TransactionItems[i].SetUUID(buuid)
        self.TransactionItems[i].show()
      else:
        self.NewTransaction(buuid)

  def NewTransaction(self, buuid):
    self.TransactionItems.append(PersonalBillsItemWidget(self.DataHandlerObject, buuid, self))
    self.Grid.addWidget(self.TransactionItems[-1], len(self.TransactionItems), Qt.AlignHCenter)
