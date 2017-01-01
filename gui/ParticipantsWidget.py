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
    self.Grid.addWidget(QLabel("<b>List</b>", self), 0, 0, 1, 2, Qt.AlignHCenter)

    self.ListWidget = QListWidget(self)
    self.ListWidget.currentItemChanged.connect(lambda n, o: self.ShowParticipantInfo(n))
    self.LoadParticipants()

    self.Grid.addWidget(self.ListWidget, 1, 0, 7, 2, Qt.AlignHCenter)

    badd = QPushButton("Add")
    badd.clicked.connect(self.AddNewParticipant)
    self.Grid.addWidget(badd, 8, 0, 1, 1, Qt.AlignRight)

    brem = QPushButton("Remove")
    brem.clicked.connect(self.RemoveParticipant)
    self.Grid.addWidget(brem, 8, 1, 1, 1, Qt.AlignLeft)

    self.Grid.addWidget(QLabel("<b>Information</b>", self), 0, 2, 1, 2, Qt.AlignHCenter)

    self.Grid.addWidget(QLabel("Name:", self), 1, 2, 1, 1, Qt.AlignRight)
    self.LineEditName = QLineEdit(self)
    self.Grid.addWidget(self.LineEditName, 1, 3, 1, 1, Qt.AlignLeft)

    self.Grid.addWidget(QLabel("At home:", self), 2, 2, 1, 1, Qt.AlignRight)
    self.CheckBoxHome = QCheckBox(self)
    self.CheckBoxHome.setChecked(True)
    self.Grid.addWidget(self.CheckBoxHome, 2, 3, 1, 1, Qt.AlignLeft)

    self.Grid.addWidget(QLabel("Can do chores:", self), 3, 2, 1, 1, Qt.AlignRight)
    self.CheckBoxCanDo = QCheckBox(self)
    self.CheckBoxCanDo.setChecked(True)
    self.Grid.addWidget(self.CheckBoxCanDo, 3, 3, 1, 1, Qt.AlignLeft)

    self.Grid.addWidget(QLabel("<b>Extra information</b>", self), 4, 2, 1, 2, Qt.AlignHCenter)

    self.Grid.addWidget(QLabel("Creation date:", self), 5, 2, 1, 1, Qt.AlignRight)
    self.LabelCreation = QLabel("(not yet set)", self)
    self.Grid.addWidget(self.LabelCreation, 5, 3, 1, 1, Qt.AlignLeft)

    self.Grid.addWidget(QLabel("UUID:", self), 6, 2, 1, 1, Qt.AlignRight)
    self.LabelUUID = QLabel("(not yet set)", self)
    self.Grid.addWidget(self.LabelUUID, 6, 3, 1, 1, Qt.AlignLeft)

    bsave = QPushButton("Save")
    bsave.clicked.connect(self.SaveParticipant)
    self.Grid.addWidget(bsave, 8, 3, 1, 1, Qt.AlignLeft)

    dummy = QWidget()
    dummy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.Grid.addWidget(dummy,7,2,1,2)

  def LoadParticipants(self):
    self.ListWidget.clear()
    for uuid, name in self.DataHandlerObject.SortedParticipantsList:
      self.ListWidget.addItem(ParticipantListItem(self.DataHandlerObject.GetItem('participants', uuid), name, self.ListWidget))

  def ShowParticipantInfo(self, item):
    if item == None: return
    self.LineEditName.setText(str(item.ParticipantData["name"]))
    self.CheckBoxHome.setChecked(item.ParticipantData["athome"])
    self.CheckBoxCanDo.setChecked(item.ParticipantData["cando"])
    self.LabelCreation.setText(item.ParticipantData["timestamp"])
    self.LabelUUID.setText(item.ParticipantData["uuid"])

  def AddNewParticipant(self):
    self.ListWidget.setCurrentItem(None)
    self.LineEditName.setText("")
    self.CheckBoxHome.setChecked(True)
    self.CheckBoxCanDo.setChecked(True)
    self.LabelCreation.setText("(not yet set)")
    self.LabelUUID.setText("(not yet set)")
    self.LoadParticipants()

  def SaveParticipant(self):
    if (self.ListWidget.currentItem()):
      self.DataHandlerObject.EditItem("participants", self.ListWidget.currentItem().ParticipantData['uuid'], {"name": self.LineEditName.text(), "athome": self.CheckBoxHome.isChecked(), 'cando' :
      self.CheckBoxCanDo.isChecked()})
    else:
      self.DataHandlerObject.AddNewItem("participants", {"name": self.LineEditName.text(), "athome": self.CheckBoxHome.isChecked(), 'cando' :
      self.CheckBoxCanDo.isChecked()})
    self.LoadParticipants()

  def RemoveParticipant(self):
    self.DataHandlerObject.RemoveItem("participants", self.ListWidget.currentItem().ParticipantData['uuid'])
    self.LoadParticipants()
