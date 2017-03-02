# -*- coding: utf8 -*-
import functools

from datahandler import *
from .TransactionWidget import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

"""
  Personal bills item widget
"""

class PersonalBillsItemWidget(QFrame):
  def __init__(self, dho, buuid, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QGridLayout(self)

    self.buuid = buuid

    self.setFixedSize(1200, 90)
    self.setFrameStyle(QFrame.Plain | QFrame.StyledPanel)

    self.Grid.addWidget(QLabel('<b>Name</b>', self), 0, 0, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Shopping</b>', self), 1, 0, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Creation date</b>', self), 2, 0, Qt.AlignRight)

    self.Grid.addWidget(QLabel('<b>Contribution</b>', self), 0, 2, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Chores</b>', self), 1, 2, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Date interval</b>', self), 2, 2, Qt.AlignRight)

    self.Grid.addWidget(QLabel('<b>Recurring</b>', self), 0, 4, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Shared shopping</b>', self), 1, 4, Qt.AlignRight)

    self.Grid.addWidget(QLabel('<b>Subtotal</b>', self), 1, 6, Qt.AlignHCenter)

    #'%Y-%m-%d %H:%M:%S.%f')

    self.Inputs = {
      'name' : [
        QLabel('', self), (0, 1, Qt.AlignLeft)
      ],

      'personal_shopping_costs' : [
        QLabel('0.00€', self), (1, 1, Qt.AlignLeft)
      ],

      'date' : [
        QLabel('', self), (2, 1, Qt.AlignLeft)
      ],

      'contribution' : [
        QLabel('0.00€', self), (0, 3, Qt.AlignLeft)
      ],

      'chores' : [
        QLabel('0.00€', self), (1, 3, Qt.AlignLeft)
      ],

      'date_range' : [
        QLabel('', self), (2, 3, Qt.AlignLeft)
      ],

      'shared_shopping_costs' : [
        QLabel('0.00€', self), (0, 5, Qt.AlignLeft)
      ],

      'recurring' : [
        QLabel('0.00€', self), (1, 5, Qt.AlignLeft)
      ],

      'subtotal' : [
        QLabel('0.00€', self), (0, 6, Qt.AlignHCenter),
        lambda q: (
          q.setFont(QFont('Arial', 24, 0)),
        )
      ],

      'delete' : [
        QPushButton('', self), (0, 7, Qt.AlignRight),
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

  def Update(self):
    if self.buuid is None: return

    self.BillData = self.DataHandlerObject.BillingData['bills'][self.buuid]['bill_data']

    self.Inputs['name'][0].setText(self.DataHandlerObject.GetItemKey('participants', self.DataHandlerObject.BillingData['bills'][self.buuid]['puuid'], 'name'))

    self.Inputs['date'][0].setText(self.DataHandlerObject.BillingData['bills'][self.buuid]['timestamp'])

    self.Inputs['date_range'][0].setText('%s to %s' % [datetime.date(*d) for d in self.DataHandlerObject.BillingData['bills'][self.buuid]['date_range']])

    for key in self.BillData:
      if key in self.Inputs:
        self.Inputs[key][0].setText(u'%2.2f€' % self.BillData[key])

  def SetUUID(self, new_buuid):
    self.buuid = new_buuid
    self.Update()

  def Delete(self):
    self.hide()

    self.DataHandlerObject.BillingRemoveItem('bills', self.buuid)
    self.buuid = None

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

  def LoadTransactions(self, py_date0, py_date1):
    for widget in self.TransactionItems:
      widget.hide()

    relevant_tuuids = self.DataHandlerObject.BillingGetItemsInRange(self.tkey, py_date0, py_date1)

    for i, tuuid in enumerate(relevant_tuuids):
      if i < len(self.TransactionItems):
        self.TransactionItems[i].SetUUID(tuuid)
        self.TransactionItems[i].show()
      else:
        self.NewTransaction(tuuid)

  def NewTransaction(self, tuuid):
    self.TransactionItems.append(PersonalBillsItemWidget(self.DataHandlerObject, tuuid, self))
    self.Grid.addWidget(self.TransactionItems[-1], len(self.TransactionItems), Qt.AlignHCenter)
