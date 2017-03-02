# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

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
        self.Inputs[key][0].setText(u'%2.2f€' % self.BillData[key])

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

class BillingWidget(QWidget):
  def __init__(self, name, parent, dho):
    super().__init__(parent.TabBox)
    self.DataHandlerObject = dho

    self.Grid = QGridLayout(self)
    self.Grid.setSpacing(10)

    self.Parent = parent
    self.Name = name

    """
      Date range
    """

    self.DateWidget = QWidget(self)
    self.DateBox = QHBoxLayout(self.DateWidget)
    self.Grid.addWidget(self.DateWidget, 0, 0, 1, 3, Qt.AlignHCenter)

    self.DateBox.addWidget(QLabel('Choose date interval:', self.DateWidget), 0, Qt.AlignLeft)

    self.DateInterval = [QDateEdit(QDate(datetime.date.today() - datetime.timedelta(days=60)), self.DateWidget), QDateEdit(QDate(datetime.date.today()), self.DateWidget)]

    for i, DE in enumerate(self.DateInterval):
      DE.setDisplayFormat('yyyy-MM-dd')
      self.DateBox.addWidget(DE, i + 1, Qt.AlignHCenter)

    bupdate = QPushButton('Update', self)
    bupdate.clicked.connect(self.Update)
    self.DateBox.addWidget(bupdate, len(self.DateInterval) + 1)

    """
      Left frame layout
    """

    self.CommonCostWidget = QWidget(self)
    self.CommonCostBox = QGridLayout(self.CommonCostWidget)
    self.Grid.addWidget(self.CommonCostWidget, 1, 0, 1, 1, Qt.AlignHCenter)

    dummy = QWidget()
    dummy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.CommonCostBox.addWidget(dummy,100,0)

    """
      Shared expenses
    """

    self.CommonCostBox.addWidget(QLabel('<b>Shared expenses</b> <i>(per person)</i>', self.CommonCostWidget), 0, 0, 1, 2, Qt.AlignHCenter)

    self.CommonCostBox.addWidget(QLabel('<b>Recurring</b>', self.CommonCostWidget), 1, 0, 1, 1, Qt.AlignHCenter)

    self.LineEditRecExp = QLineEdit(self.CommonCostWidget)
    self.LineEditRecExp.setValidator(QRegExpValidator(QRegExp('\-?\d{1,3}.\d{1,2}'), self))
    self.CommonCostBox.addWidget(self.LineEditRecExp, 1, 1, Qt.AlignHCenter)

    self.CommonCostBox.addWidget(QLabel('<b>Shopping</b>', self.CommonCostWidget), 2, 0, 1, 1, Qt.AlignHCenter)

    self.SharedShoppingCosts = 0.0
    self.LabelShopCost = QLabel('0.00€', self.CommonCostWidget)
    self.CommonCostBox.addWidget(self.LabelShopCost, 2, 1, Qt.AlignHCenter)
    self.ComputeSharedShoppingCosts()

    """
      Bank information
    """

    self.CommonCostBox.addWidget(QLabel('<b>Bank information</b>', self.CommonCostWidget), 3, 0, 2, 2, Qt.AlignHCenter)

    self.CommonCostBox.addWidget(QLabel('<b>Bank name</b>', self.CommonCostWidget), 5, 0, 1, 1, Qt.AlignHCenter)

    self.LineEditBankName = QLineEdit(self.CommonCostWidget)
    self.CommonCostBox.addWidget(self.LineEditBankName, 5, 1, Qt.AlignHCenter)

    self.CommonCostBox.addWidget(QLabel('<b>Account No.</b>', self.CommonCostWidget), 6, 0, 1, 1, Qt.AlignHCenter)

    self.LineEditAccNo = QLineEdit(self.CommonCostWidget)
    self.CommonCostBox.addWidget(self.LineEditAccNo, 6, 1, Qt.AlignHCenter)

    self.CommonCostBox.addWidget(QLabel('<b>Account holder</b>', self.CommonCostWidget), 7, 0, 1, 1, Qt.AlignHCenter)

    self.LineEditAccHolder = QLineEdit(self.CommonCostWidget)
    self.CommonCostBox.addWidget(self.LineEditAccHolder, 7, 1, Qt.AlignHCenter)

    self.CommonCostBox.addWidget(QLabel('<b>Location</b>', self.CommonCostWidget), 8, 0, 1, 1, Qt.AlignHCenter)

    self.LineEditLoc = QLineEdit(self.CommonCostWidget)
    self.CommonCostBox.addWidget(self.LineEditLoc, 8, 1, Qt.AlignHCenter)

    bsave = QPushButton('Save', self.CommonCostWidget)
    bsave.clicked.connect(self.SaveInformation)
    self.CommonCostBox.addWidget(bsave, 9, 0, 1, 1, Qt.AlignHCenter)

    bgenbill = QPushButton('Generate Bill', self.CommonCostWidget)
    bgenbill.clicked.connect(self.SaveInformation)
    self.CommonCostBox.addWidget(bgenbill, 9, 1, 1, 1, Qt.AlignHCenter)

    self.BillStatus = QLabel('', self.CommonCostWidget)
    self.CommonCostBox.addWidget(self.BillStatus, 10, 0, 1, 2, Qt.AlignHCenter)

    self.LoadInformation()

    """
      Balance information
    """

    self.BalanceWidget = ParticipantsBalanceWidget(self.DataHandlerObject, self)

    self.BalanceScroll = QScrollArea(self)
    self.BalanceScroll.setWidget(self.BalanceWidget)
    self.BalanceScroll.setAlignment(Qt.AlignHCenter)
    self.BalanceScroll.setFixedSize(900, 700)
    self.Grid.addWidget(self.BalanceScroll, 1, 1, 1, 2, Qt.AlignHCenter)

    self.Update()

  def SaveInformation(self):
    new_data = {
      'recurring' : float(self.LineEditRecExp.text()),
      'bank_name' : self.LineEditBankName.text(),
      'acc_no' : self.LineEditAccNo.text(),
      'acc_holder' : self.LineEditAccHolder.text(),
      'loc' : self.LineEditLoc.text()
    }

    self.DataHandlerObject.BillingData['config'].update(new_data)
    self.DataHandlerObject.UpdateBillingFile()

  def LoadInformation(self):
    self.LineEditRecExp.setText('%2.2f' % self.DataHandlerObject.BillingData['config']['recurring'])
    self.LineEditBankName.setText(self.DataHandlerObject.BillingData['config']['bank_name'])
    self.LineEditAccNo.setText(self.DataHandlerObject.BillingData['config']['acc_no'])
    self.LineEditAccHolder.setText(self.DataHandlerObject.BillingData['config']['acc_holder'])
    self.LineEditLoc.setText(self.DataHandlerObject.BillingData['config']['loc'])

  def ComputeSharedShoppingCosts(self):
    py_dates = [qd.date().toPyDate() for qd in self.DateInterval]
    relevant_tuuids = self.DataHandlerObject.BillingGetItemsInRange('expenses', *py_dates)

    s = 0.0
    for tuuid in relevant_tuuids:
      s += self.DataHandlerObject.BillingData['expenses'][tuuid]['amount']
    s /= len(self.DataHandlerObject.SortedParticipantsList)

    self.SharedShoppingCosts = s
    self.LabelShopCost.setText('%2.2f€' % s)

  def GenerateBill(self):
    group_data = {
      'date_range' : [list(qd.date().toPyDate().timetuple())[:3] for qd in self.DateInterval],
      'buuids' : []
    }

    gbuuid = self.DataHandlerObject.BillingAddNewItem('group_bills', group_data)

    bill_data = {
      'date_range' : [list(qd.date().toPyDate().timetuple())[:3] for qd in self.DateInterval],
      'puuid' : '',
      'bill_data' : {},
      'gbuuid' : gbuuid
    }

    for widget in self.BillingWidget.ParticipantItems:
      bill_data['puuid'] = widget.puuid
      bill_data['bill_data'] = widget.BillData

      group_data['buuids'].append(self.DataHandlerObject.BillingAddNewItem('bills', copy.deepcopy(bill_data)))

    self.DataHandlerObject.BillingEditItem('group_bills', gbuuid, group_data)

  def Update(self):
    self.ComputeSharedShoppingCosts()
    self.BalanceWidget.Update([qd.date().toPyDate() for qd in self.DateInterval], self.SharedShoppingCosts)
