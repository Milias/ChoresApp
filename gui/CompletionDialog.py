# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

class AssignmentTreeItem(QTreeWidgetItem):
  def __init__(self, dho, key, auuid, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.auuid = auuid
    self.key = key

    self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    self.Update()

  def Update(self):
    self.setText(0, self.DataHandlerObject.GetItemKey('chores', self.DataHandlerObject.TempWeekAsignment[self.key][self.auuid]['choreuuid'], 'name'))

    if self.key == 'normal':
      self.setText(1, self.DataHandlerObject.GetItemKey('participants', self.DataHandlerObject.TempWeekAsignment['normal'][self.auuid]['personuuid'], 'name'))
    else:
      self.setText(1, '(anyone)')

    datecomp = self.DataHandlerObject.TempWeekAsignment[self.key][self.auuid]['datecomp']
    if len(datecomp):
      self.setText(2, '%s' % datetime.date(*datecomp))
    else:
       self.setText(2, '')

    puuidcomp = self.DataHandlerObject.TempWeekAsignment[self.key][self.auuid]['puuidcomp']
    if len(puuidcomp):
      self.setText(3, ', '.join([self.DataHandlerObject.GetItemKey('participants', uuid, 'name') for uuid in self.DataHandlerObject.TempWeekAsignment[self.key][self.auuid]['puuidcomp']]))
    else:
       self.setText(3, '')


class CompletionDialog(QDialog):
  def __init__(self, dho, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho

    self.setWindowTitle('Set completion information')
    self.Grid = QGridLayout()
    self.Grid.setSpacing(10)
    self.setLayout(self.Grid)

    self.Grid.addWidget(QLabel('<b>Select assignment:</b>', self), 0, 0, 1, 6, Qt.AlignHCenter)
    self.TAssignments = QTreeWidget(self)
    self.TAssignments.setMinimumSize(960,480)
    self.TAssignments.setColumnCount(4)
    self.TAssignments.setHeaderLabels(['Chore', 'Assigned Person', 'Date', 'Name'])
    for i, w in enumerate([460, 100, 150, 250]):
      self.TAssignments.setColumnWidth(i, w)
    self.TAssignments.setSortingEnabled(True)
    self.TAssignments.sortByColumn(1, Qt.AscendingOrder)
    self.TAssignments.setSelectionMode(QAbstractItemView.ExtendedSelection)
    self.TAssignments.itemSelectionChanged.connect(self.UpdateSelection)
    self.Grid.addWidget(self.TAssignments, 1, 0, 1, 6, Qt.AlignHCenter)

    self.TITopCats = {}
    self.TIAssignmentChildren = []
    for key, name in [('normal', 'Normal'), ('other', 'Other')]:
      self.TITopCats[key] = QTreeWidgetItem(self.TAssignments, [name])
      self.TITopCats[key].setFlags(Qt.ItemIsEnabled)
      self.TAssignments.addTopLevelItem(self.TITopCats[key])
      for auuid in self.DataHandlerObject.TempWeekAsignment[key]:
        self.TIAssignmentChildren.append(AssignmentTreeItem(self.DataHandlerObject, key, auuid, self.TITopCats[key]))
        self.TITopCats[key].addChild(self.TIAssignmentChildren[-1])

    self.TAssignments.expandAll()

    self.Grid.addWidget(QLabel('Completion date:', self), 2, 0, 1, 1, Qt.AlignRight)
    self.DateEditComp = QDateEdit(QDate(datetime.date.today()), self)
    self.Grid.addWidget(self.DateEditComp, 2, 1, 1, 1, Qt.AlignLeft)

    self.Grid.addWidget(QLabel('Person(s):', self), 2, 2, 1, 1, Qt.AlignRight)
    self.CBoxPerson = QComboBox(self)
    self.Grid.addWidget(self.CBoxPerson, 2, 3, 1, 1, Qt.AlignLeft)
    self.CBoxPerson.addItem('(add/remove all)')
    for pid, name in self.DataHandlerObject.SortedParticipantsList:
      self.CBoxPerson.addItem(name)

    bcomp = QPushButton('Add', self)
    bcomp.clicked.connect(self.AddSelection)
    self.Grid.addWidget(bcomp, 2, 4, 1, 1, Qt.AlignHCenter)

    bcomp = QPushButton('Remove', self)
    bcomp.clicked.connect(self.RemoveSelection)
    self.Grid.addWidget(bcomp, 2, 5, 1, 1, Qt.AlignHCenter)

  def UpdateSelection(self):
    if len(self.TAssignments.selectedItems()) == 0: return
    datecomp = self.DataHandlerObject.TempWeekAsignment[self.TAssignments.selectedItems()[0].key][self.TAssignments.selectedItems()[0].auuid]['datecomp']
    if datecomp != []:
      self.DateEditComp.setDate(QDate(*datecomp))
    else:
      self.DateEditComp.setDate(QDate(datetime.date.today()))

  def AddSelection(self):
    if self.CBoxPerson.currentIndex():
      current_puuid = self.DataHandlerObject.SortedParticipantsList[self.CBoxPerson.currentIndex()-1][0]

    for item in self.TAssignments.selectedItems():
      if self.CBoxPerson.currentIndex():
        new_data = {
          'uuid' : item.auuid,
          'datecomp' : list(self.DateEditComp.date().getDate()),
          'puuidcomp' : list(set(self.DataHandlerObject.TempWeekAsignment[item.key][item.auuid]['puuidcomp'] + [current_puuid]))
        }
      else:
        new_data = {
          'uuid' : item.auuid,
          'datecomp' : list(self.DateEditComp.date().getDate()),
          'puuidcomp' : list(set(self.DataHandlerObject.TempWeekAsignment[item.key][item.auuid]['puuidcomp'] + [t[0] for t in self.DataHandlerObject.SortedParticipantsList]))
        }
      self.DataHandlerObject.TempEditChore(item.key, new_data)

    for item in self.TIAssignmentChildren: item.Update()

  def RemoveSelection(self):
    if self.CBoxPerson.currentIndex():
      current_puuid = self.DataHandlerObject.SortedParticipantsList[self.CBoxPerson.currentIndex()-1][0]

    for item in self.TAssignments.selectedItems():
      if self.CBoxPerson.currentIndex():
        new_puuidcomp = self.DataHandlerObject.TempWeekAsignment[item.key][item.auuid]['puuidcomp']
        if current_puuid in new_puuidcomp:
          new_puuidcomp.remove(current_puuid)
        new_data = {
          'uuid' : item.auuid,
          'datecomp' : self.DataHandlerObject.TempWeekAsignment[item.key][item.auuid]['datecomp'] if len(new_puuidcomp) else [],
          'puuidcomp' : new_puuidcomp
        }
      else:
        new_data = {
          'uuid' : item.auuid,
          'datecomp' : [],
          'puuidcomp' : []
        }

      self.DataHandlerObject.TempEditChore(item.key, new_data)

    for item in self.TIAssignmentChildren: item.Update()
