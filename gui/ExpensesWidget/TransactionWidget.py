# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

"""
  Transaction Widgets - Item and ScrollArea
"""

class TransactionsItemWidget(QFrame):
  def __init__(self, dho, tkey, tuuid, parent, edit_mode = False):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QGridLayout(self)

    self.tkey = tkey
    self.tuuid = tuuid
    self.EditMode = edit_mode

    self.setFixedSize(1200, 90)
    self.setFrameStyle(QFrame.Plain | QFrame.StyledPanel)

    self.Grid.addWidget(QLabel('<b>Name</b>', self), 0, 0, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Date</b>', self), 0, 2, Qt.AlignRight)
    self.Grid.addWidget(QLabel('<b>Description</b>', self), 1, 0, Qt.AlignRight)

    self.Inputs = {
      'name' : [
        QLabel('', self), QComboBox(self), (0, 1, Qt.AlignLeft),
        lambda q:
          [q[1].addItem(e[1]) for e in self.DataHandlerObject.SortedParticipantsList]
      ],

      'date' : [
        QLabel('', self), QDateEdit(QDate(datetime.date.today()), self), (0, 3, Qt.AlignHCenter),
        lambda q: (
            q[1].setDisplayFormat('yyyy-MM-dd')
          )
      ],

      'descr' : [
        QLabel('', self), QLineEdit('', self), (1, 1, 1, 4, Qt.AlignLeft),
        lambda q: (
          q[0].setFixedWidth(550),
          q[1].setFixedWidth(550)
        )
      ],

      'amount' : [
        QLabel('0.00€', self), QLineEdit('0.00', self), (0, 4, 2, 1, Qt.AlignHCenter),
        lambda q: (
          q[0].setFont(QFont('Arial', 28, 0)),
          q[0].setFixedHeight(60),
          q[1].setValidator(QRegExpValidator(QRegExp('\-?\d{1,3}.\d{1,2}'), self)),
          q[1].setAlignment(Qt.AlignHCenter),
          q[1].setFrame(False),
          q[1].setFont(QFont('Arial', 28, 0)),
          q[1].setFixedSize(200, 60)
        )
      ],

      'edit' : [
        QPushButton('', self), QPushButton('', self), (0, 5, Qt.AlignRight),
        lambda q: (
          q[0].setIcon(QIcon('gui/icons/edit.svg')),
          q[0].setIconSize(QSize(32, 32)),
          q[0].setFixedSize(32, 32),
          q[0].clicked.connect(lambda: self.SetEditMode(True)),
          q[1].setIcon(QIcon('gui/icons/check.svg')),
          q[1].setIconSize(QSize(32, 32)),
          q[1].setFixedSize(32, 32),
          q[1].clicked.connect(lambda: self.SetEditMode(False))
        )
      ],

      'delete' : [
        QPushButton('', self), QPushButton('', self), (1, 5, Qt.AlignRight),
        lambda q: (
          q[0].setIcon(QIcon('gui/icons/delete.svg')),
          q[0].setIconSize(QSize(32, 32)),
          q[0].setFixedSize(32, 32),
          q[0].clicked.connect(self.DeleteTransaction),
          q[1].setIcon(QIcon('gui/icons/delete.svg')),
          q[1].setIconSize(QSize(32, 32)),
          q[1].setFixedSize(32, 32),
          q[1].clicked.connect(self.DeleteTransaction)
        )
      ]
    }

    for key in self.Inputs:
      self.Inputs[key][not self.EditMode].hide()
      if len(self.Inputs[key]) > 3:
        self.Inputs[key][3](self.Inputs[key][:2])
      for widget in self.Inputs[key][:2]:
        self.Grid.addWidget(widget, *self.Inputs[key][2])

    self.Update()

  def UpdateTUUID(self, new_tuuid):
    self.tuuid = new_tuuid
    self.Update()

  def DeleteTransaction(self):
    self.hide()

    self.SetEditMode(False)
    self.DataHandlerObject.BillingRemoveItem(self.tkey, self.tuuid)
    self.tuuid = None

  def SetEditMode(self, edit_mode = True):
    if self.tuuid is None: return

    for key in self.Inputs:
      self.Inputs[key][self.EditMode].hide()
      self.Inputs[key][edit_mode].show()
    self.EditMode = edit_mode

    if not self.EditMode:
      new_data = {
        'puuid' :       self.DataHandlerObject.SortedParticipantsList[self.Inputs['name'][1].currentIndex()][0],
        'date' : list(self.Inputs['date'][1].date().getDate()),
        'descr' : self.Inputs['descr'][1].text(),
        'amount' : float(self.Inputs['amount'][1].text())
      }
      self.DataHandlerObject.BillingEditItem(self.tkey, self.tuuid, new_data)
    self.Update()

  def Update(self):
    if self.tuuid is None: return

    self.Inputs['name'][0].setText(
      self.DataHandlerObject.GetItemKey(
        'participants',
        self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['puuid'],
        'name'
      )
    )

    date = self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['date']
    self.Inputs['date'][0].setText('%s' % datetime.date(*date))

    self.Inputs['descr'][0].setText(self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['descr'])

    amount = self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['amount']
    self.Inputs['amount'][0].setText(u'%.2f€' % amount)

    self.Inputs['name'][1].setCurrentIndex(
      self.DataHandlerObject.SortedParticipantsList.index((
      self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['puuid'],
      self.DataHandlerObject.GetItemKey(
        'participants',
        self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['puuid'],
        'name'
      )))
    )

    date = self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['date']
    self.Inputs['date'][1].setDate(QDate(*date))

    self.Inputs['descr'][1].setText(self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['descr'])

    amount = self.DataHandlerObject.BillingData[self.tkey][self.tuuid]['amount']
    self.Inputs['amount'][1].setText('%.2f' % amount)

class TransactionsWidget(QWidget):
  def __init__(self, dho, tkey, parent, can_add = True):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.Grid = QVBoxLayout(self)
    self.Grid.setAlignment(Qt.AlignHCenter)

    self.Grid.setSizeConstraint(QLayout.SetMinAndMaxSize)

    self.tkey = tkey
    self.CanAdd = can_add

    self.TransactionItems = []

    if can_add: self.CreateAddButton()

  def CreateAddButton(self):
    self.ButtonAdd = QPushButton('', self)
    self.ButtonAdd.setIcon(QIcon('gui/icons/add.svg'))
    self.ButtonAdd.setIconSize(QSize(48, 48))
    self.ButtonAdd.setFixedSize(1200, 56)
    self.ButtonAdd.clicked.connect(
      lambda:  self.NewTransaction(
        self.DataHandlerObject.BillingAddNewItem(
          self.tkey,
          {
            'puuid' : self.DataHandlerObject.SortedParticipantsList[0][0],
            'date' : list(datetime.date.today().timetuple())[:3],
            'descr' : '',
            'amount' : 0.0
          }
        )
      )
    )

    self.Grid.addWidget(self.ButtonAdd, 100, Qt.AlignHCenter)

  def LoadTransactions(self, py_date0, py_date1):
    for widget in self.TransactionItems:
      widget.SetEditMode(False)
      widget.hide()

    relevant_tuuids = self.DataHandlerObject.BillingGetItemsInRange(self.tkey, py_date0, py_date1)

    for i, tuuid in enumerate(relevant_tuuids):
      if i < len(self.TransactionItems):
        self.TransactionItems[i].UpdateTUUID(tuuid)
        self.TransactionItems[i].show()
      else:
        self.NewTransaction(tuuid, False)

  def NewTransaction(self, tuuid, edit_mode = True):
    self.TransactionItems.append(TransactionsItemWidget(self.DataHandlerObject, self.tkey, tuuid, self, edit_mode))

    self.Grid.addWidget(self.TransactionItems[-1], len(self.TransactionItems), Qt.AlignHCenter)
