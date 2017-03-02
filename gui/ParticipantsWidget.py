# -*- coding: utf8 -*-
from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

class ParticipantListItem(QListWidgetItem):
  def __init__ (self, cd, text, parent = None, type = QListWidgetItem.Type):
    super().__init__(text, parent, type)
    self.ParticipantData = cd

class ParticipantsWidget(QWidget):
  def __init__(self, name, parent, dho):
    super().__init__(parent.TabBox)
    self.DataHandlerObject = dho

    self.Grid = QGridLayout()
    self.Grid.setSpacing(10)
    self.setLayout(self.Grid)

    self.Parent = parent
    self.Name = name
    self.Init()

  def Init(self):
    self.Grid.addWidget(QLabel('<b>List</b>', self), 0, 0, 1, 2, Qt.AlignHCenter)

    self.ListWidget = QListWidget(self)
    self.ListWidget.currentItemChanged.connect(lambda n, o: self.ShowParticipantInfo(n))
    self.ListWidget.setFixedSize(400, 700)
    self.LoadParticipants()

    self.Grid.addWidget(self.ListWidget, 1, 0, 10, 2, Qt.AlignHCenter)

    badd = QPushButton('Add')
    badd.clicked.connect(self.AddNewParticipant)
    self.Grid.addWidget(badd, 11, 0, 1, 1, Qt.AlignRight)

    brem = QPushButton('Remove')
    brem.clicked.connect(self.RemoveParticipant)
    self.Grid.addWidget(brem, 11, 1, 1, 1, Qt.AlignLeft)

    nrow = 0
    self.Grid.addWidget(QLabel('<b>Information</b>', self), nrow, 2, 1, 2, Qt.AlignHCenter)
    nrow += 1

    self.Grid.addWidget(QLabel('Name:', self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditName = QLineEdit(self)
    self.Grid.addWidget(self.LineEditName, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel('At home:', self), nrow, 2, 1, 1, Qt.AlignRight)
    self.CheckBoxHome = QCheckBox(self)
    self.CheckBoxHome.setChecked(True)
    self.Grid.addWidget(self.CheckBoxHome, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel('<b>Billing information</b>', self), nrow, 2, 1, 2, Qt.AlignHCenter)
    nrow += 1

    self.Grid.addWidget(QLabel('Contribution:', self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditContr = QLineEdit(self)
    self.LineEditContr.setValidator(QRegExpValidator(QRegExp('\-?\d{1,3}.\d{1,2}'), self))
    self.Grid.addWidget(self.LineEditContr, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel('Balance offset:', self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditBalanceOffset = QLineEdit(self)
    self.LineEditBalanceOffset.setValidator(QRegExpValidator(QRegExp('\-?\d{1,3}.\d{1,2}'), self))
    self.Grid.addWidget(self.LineEditBalanceOffset, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel('<b>Extra information</b>', self), nrow, 2, 1, 2, Qt.AlignHCenter)
    nrow += 1

    self.Grid.addWidget(QLabel('Creation date:', self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LabelCreation = QLabel('(not yet set)', self)
    self.Grid.addWidget(self.LabelCreation, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel('UUID:', self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LabelUUID = QLabel('(not yet set)', self)
    self.Grid.addWidget(self.LabelUUID, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    bsave = QPushButton('Save')
    bsave.clicked.connect(self.SaveParticipant)
    self.Grid.addWidget(bsave, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    dummy = QWidget()
    dummy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.Grid.addWidget(dummy,nrow,2,1,2)

  def LoadParticipants(self):
    self.ListWidget.clear()
    for uuid, name in self.DataHandlerObject.SortedParticipantsList:
      self.ListWidget.addItem(ParticipantListItem(self.DataHandlerObject.GetItem('participants', uuid), name, self.ListWidget))

  def ShowParticipantInfo(self, item):
    if item == None: return
    self.LineEditName.setText(item.ParticipantData['name'])
    self.CheckBoxHome.setChecked(item.ParticipantData['athome'])
    self.LineEditContr.setText('%2.2f' % item.ParticipantData['contribution'])
    self.LineEditBalanceOffset.setText('%2.2f' % item.ParticipantData['boffset'])
    self.LabelCreation.setText(item.ParticipantData['timestamp'])
    self.LabelUUID.setText(item.ParticipantData['uuid'])

  def AddNewParticipant(self):
    self.ListWidget.setCurrentItem(None)
    self.LineEditName.setText('')
    self.CheckBoxHome.setChecked(True)
    self.LineEditContr.setText('0.00')
    self.LineEditBalanceOffset.setText('0.00')
    self.LabelCreation.setText('(not yet set)')
    self.LabelUUID.setText('(not yet set)')
    self.LoadParticipants()

  def SaveParticipant(self):
    if (self.ListWidget.currentItem()):
      self.DataHandlerObject.EditItem('participants', self.ListWidget.currentItem().ParticipantData['uuid'], {'name': self.LineEditName.text(), 'athome': self.CheckBoxHome.isChecked(), 'contribution' : float(self.LineEditContr.text()), 'boffset' : float(self.LineEditBalanceOffset.text())})
    else:
      self.DataHandlerObject.AddNewItem('participants', {'name': self.LineEditName.text(), 'athome': self.CheckBoxHome.isChecked(), 'contribution' : float(self.LineEditContr.text()), 'boffset' : float(self.LineEditBalanceOffset.text())})
    self.LoadParticipants()

  def RemoveParticipant(self):
    self.DataHandlerObject.RemoveItem('participants', self.ListWidget.currentItem().ParticipantData['uuid'])
    self.LoadParticipants()
