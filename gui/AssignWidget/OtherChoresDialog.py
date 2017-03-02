# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

class OtherChoreTreeItem(QTreeWidgetItem):
  def __init__(self, dho, uuid, auuid, cdate, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.uuid = uuid
    self.auuid = auuid
    self.cdate = cdate

    self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    self.Update()

  def Update(self):
    self.setText(0, self.DataHandlerObject.GetItemKey('chores', self.uuid, 'name'))

    if not self.DataHandlerObject.TempCheckChore(self.uuid) and self.DataHandlerObject.GetWeekDifference(self.cdate, self.uuid) >= self.DataHandlerObject.GetItemKey('chores', self.uuid, 'freq'):
      for i in range(4): self.setBackground(i, QBrush(QColor(52, 152, 219, 96)))
    else:
      self.setBackground(0, QBrush(QColor(255, 255, 255, 255)))

    self.setText(1, str(self.DataHandlerObject.GetItemKey('chores', self.uuid, 'freq')))

    self.setText(2, self.DataHandlerObject.GetItemKey('chores', self.uuid, 'alast'))

    self.setText(3, str(self.DataHandlerObject.GetWeekDifference(self.cdate, self.uuid)))

class OtherChoresDialog(QDialog):
  def __init__(self, dho, cdate, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.cdate = cdate

    self.setWindowTitle('Add other chores')
    self.Grid = QGridLayout()
    self.Grid.setSpacing(10)
    self.setLayout(self.Grid)

    self.Grid.addWidget(QLabel('<b>Select chore:</b>', self), 0, 0, 1, 2, Qt.AlignHCenter)
    self.TAssignments = QTreeWidget(self)
    self.TAssignments.setMinimumSize(960,480)
    self.TAssignments.setColumnCount(4)
    self.TAssignments.setHeaderLabels(['Chore', 'Frequency', 'Last assigned', 'Weeks since'])
    for i, w in enumerate([460, 100, 250, 150]):
      self.TAssignments.setColumnWidth(i, w)
    self.TAssignments.setSortingEnabled(True)
    self.TAssignments.sortByColumn(3, Qt.DescendingOrder)
    self.TAssignments.setSelectionMode(QAbstractItemView.ExtendedSelection)
    self.Grid.addWidget(self.TAssignments, 1, 0, 1, 2, Qt.AlignHCenter)

    self.TIAssignmentChildren = []
    for uuid in self.DataHandlerObject.ConfigData['chores']:
      self.TIAssignmentChildren.append(OtherChoreTreeItem(self.DataHandlerObject, uuid, self.DataHandlerObject.TempCheckChore(uuid, ('other',)), self.cdate, self.TAssignments))
      self.TAssignments.addTopLevelItem(self.TIAssignmentChildren[-1])

    bcomp = QPushButton('Add', self)
    bcomp.clicked.connect(self.AddSelection)
    self.Grid.addWidget(bcomp, 2, 0, 1, 1, Qt.AlignHCenter)

    bcomp = QPushButton('Remove', self)
    bcomp.clicked.connect(self.RemoveSelection)
    self.Grid.addWidget(bcomp, 2, 1, 1, 1, Qt.AlignHCenter)

  def AddSelection(self):
    for item in self.TAssignments.selectedItems():
      item.auuid = self.DataHandlerObject.TempAddChore('other', item.uuid)

    for item in self.TIAssignmentChildren: item.Update()

  def RemoveSelection(self):
    for item in self.TAssignments.selectedItems():
      if item.auuid != '': self.DataHandlerObject.TempRemoveChore('other', item.auuid)

    for item in self.TIAssignmentChildren: item.Update()
