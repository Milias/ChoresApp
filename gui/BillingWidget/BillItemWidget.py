# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class ParticipantsBalanceItemWidget(QFrame):
  def __init__(self, dho, puuid, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QGridLayout(self)

    self.puuid = puuid

    self.setFixedSize(850, 90)
    self.setFrameStyle(QFrame.Plain | QFrame.StyledPanel)

    self.Grid.addWidget(QLabel('<b>Name</b>', self), 0, 0, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Contribution</b>', self), 0, 2, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Shopping</b>', self), 1, 0, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Chores</b>', self), 1, 2, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Subtotal</b>', self), 1, 4, Qt.AlignHCenter)

    self.Inputs = {
      'name' : [
        QLabel('', self), (0, 1, Qt.AlignLeft)
      ],

      'contribution' : [
        QLabel('0.00€', self), (0, 3, Qt.AlignLeft)
      ],

      'personal_shopping_costs' : [
        QLabel('0.00€', self), (1, 1, Qt.AlignLeft)
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

    self.BillData = {
      'recurring' : 0.0,
      'shared_shopping_costs' : 0.0,
      'contribution' : 0.0,
      'personal_shopping_costs' : 0.0,
      'chores' : 0.0,
      'subtotal' : 0.0
    }

  def Update(self, py_dates, chores_data, ssc):
    if self.puuid is None: return

    self.BillData['recurring'] = self.DataHandlerObject.BillingData['config']['recurring']
    self.BillData['shared_shopping_costs'] = ssc
    self.BillData['chores'] = chores_data[self.puuid]
    self.BillData['contribution'] = self.DataHandlerObject.GetItemKey('participants', self.puuid, 'contribution')

    self.BillData['personal_shopping_costs'] = 0.0
    for tuuid in self.DataHandlerObject.BillingGetItemsInRange('expenses', *py_dates):
      if self.DataHandlerObject.BillingData['expenses'][tuuid]['puuid'] == self.puuid:
        self.BillData['personal_shopping_costs'] += self.DataHandlerObject.BillingData['expenses'][tuuid]['amount']

    self.BillData['subtotal'] = self.BillData['recurring'] + self.BillData['shared_shopping_costs'] + self.BillData['contribution'] + self.BillData['chores'] - self.BillData['personal_shopping_costs']

    self.Inputs['name'][0].setText(self.DataHandlerObject.GetItemKey('participants', self.puuid, 'name'))

    for key in self.BillData:
      if key in self.Inputs:
        self.Inputs[key][0].setText(u'%.2f€' % self.BillData[key])

class ParticipantsBalanceWidget(QWidget):
  def __init__(self, dho, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QVBoxLayout(self)
    self.Grid.setAlignment(Qt.AlignHCenter)

    self.Grid.setSizeConstraint(QLayout.SetMinAndMaxSize)

    self.ParticipantItems = [ParticipantsBalanceItemWidget(self.DataHandlerObject, pid, self) for (pid, name) in self.DataHandlerObject.SortedParticipantsList]

    for i, widget in enumerate(self.ParticipantItems):
      self.Grid.addWidget(widget, i, Qt.AlignHCenter)

  def Update(self, py_dates, ssc):
    chores_data = self.DataHandlerObject.BillingGetChoresInRange(*py_dates)
    for widget in self.ParticipantItems:
      widget.Update(py_dates, chores_data, ssc)
