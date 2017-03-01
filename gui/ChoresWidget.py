# -*- coding: utf8 -*-
from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

class ChoreListItem(QListWidgetItem):
  def __init__ (self, cd, text, parent = None, type = QListWidgetItem.Type):
    super().__init__(text, parent, type)
    self.ChoreData = cd

class ChoresWidget(QWidget):
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
    self.Grid.addWidget(QLabel("<b>List</b>", self), 0, 0, 1, 2, Qt.AlignHCenter)

    self.ListWidget = QListWidget(self)
    self.ListWidget.currentItemChanged.connect(lambda n, o: self.ShowChoreInfo(n))
    self.LoadChores()

    self.Grid.addWidget(self.ListWidget, 1, 0, 9, 2, Qt.AlignHCenter)

    badd = QPushButton("Add")
    badd.clicked.connect(self.AddNewChore)
    self.Grid.addWidget(badd, 10, 0, 1, 1, Qt.AlignRight)

    brem = QPushButton("Remove")
    brem.clicked.connect(self.RemoveChore)
    self.Grid.addWidget(brem, 10, 1, 1, 1, Qt.AlignLeft)

    nrow = 0
    self.Grid.addWidget(QLabel("<b>Information</b>", self), nrow, 2, 1, 2, Qt.AlignHCenter)
    nrow += 1

    self.Grid.addWidget(QLabel("Name:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditName = QLineEdit(self)
    self.Grid.addWidget(self.LineEditName, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel("Frequency:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditFreq = QLineEdit(self)
    self.Grid.addWidget(self.LineEditFreq, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel("Priority:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditPrio = QLineEdit(self)
    self.Grid.addWidget(self.LineEditPrio, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel("Last assigned:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditLastA = QLineEdit(self)
    self.LineEditLastA.setValidator(QRegExpValidator(QRegExp("\d{1,4}\-W\d{1,2}"), self))
    self.Grid.addWidget(self.LineEditLastA, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel("Points:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LineEditPoints = QLineEdit(self)
    self.LineEditPoints.setValidator(QIntValidator())
    self.Grid.addWidget(self.LineEditPoints, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel("<b>Extra information</b>", self), nrow, 2, 1, 2, Qt.AlignHCenter)
    nrow += 1

    self.Grid.addWidget(QLabel("Creation date:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LabelCreation = QLabel("(not yet set)", self)
    self.Grid.addWidget(self.LabelCreation, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel("UUID:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LabelUUID = QLabel("(not yet set)", self)
    self.Grid.addWidget(self.LabelUUID, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    self.Grid.addWidget(QLabel("Times assigned:", self), nrow, 2, 1, 1, Qt.AlignRight)
    self.LabelTimes = QLabel("(not yet set)", self)
    self.Grid.addWidget(self.LabelTimes, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    bsave = QPushButton("Save")
    bsave.clicked.connect(self.SaveChore)
    self.Grid.addWidget(bsave, nrow, 3, 1, 1, Qt.AlignLeft)
    nrow += 1

    dummy = QWidget()
    dummy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.Grid.addWidget(dummy,9,2,1,2)

  def LoadChores(self):
    self.ListWidget.clear()
    for uuid, name in self.DataHandlerObject.SortedChoresList:
      self.ListWidget.addItem(ChoreListItem(self.DataHandlerObject.GetItem('chores', uuid), name, self.ListWidget))

  def ShowChoreInfo(self, item):
    if item == None: return
    self.LineEditName.setText(str(item.ChoreData["name"]))
    self.LineEditFreq.setText(str(item.ChoreData["freq"]))
    self.LineEditPrio.setText(str(item.ChoreData["priority"]))
    self.LineEditLastA.setText(str(item.ChoreData["alast"]))
    self.LineEditPoints.setText(str(item.ChoreData["points"]))
    self.LabelCreation.setText(item.ChoreData["timestamp"])
    self.LabelUUID.setText(item.ChoreData["uuid"])
    self.LabelTimes.setText(str(item.ChoreData["atimes"]))

  def AddNewChore(self):
    self.ListWidget.setCurrentItem(None)
    self.LineEditName.setText("")
    self.LineEditFreq.setText("")
    self.LineEditPrio.setText("")
    self.LineEditLastA.setText("0001-W1")
    self.LineEditPoints.setText("250")
    self.LabelCreation.setText("(not yet set)")
    self.LabelUUID.setText("(not yet set)")
    self.LabelTimes.setText("(not yet set)")
    self.LoadChores()

  def SaveChore(self):
    if (self.ListWidget.currentItem()):
      self.DataHandlerObject.EditItem("chores", self.ListWidget.currentItem().ChoreData['uuid'], {"name": self.LineEditName.text(), "freq": int(self.LineEditFreq.text()), "priority": int(self.LineEditPrio.text()), "alast": self.LineEditLastA.text(), "points": int(self.LineEditPoints.text())})
    else:
      self.DataHandlerObject.AddNewItem("chores", {"name": self.LineEditName.text(), "freq": int(self.LineEditFreq.text()), "priority": int(self.LineEditPrio.text()), "atimes" : 0, "alast": self.LineEditLastA.text(), "points": int(self.LineEditPoints.text())})
    self.LoadChores()

  def RemoveChore(self):
    self.DataHandlerObject.RemoveItem("chores", self.ListWidget.currentItem().ChoreData['uuid'])
    self.LoadChores()
