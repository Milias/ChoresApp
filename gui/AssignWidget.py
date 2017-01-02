# -*- coding: utf8 -*-
from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

class FrameChoresTable(QFrame):
  def __init__(self, dho, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho

    self.setFrameStyle(QFrame.Plain | QFrame.StyledPanel)
    self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.Grid = QGridLayout()
    self.Grid.setSpacing(10)
    self.setLayout(self.Grid)

    self.Init()
    self.Reset()

  def Init(self):
    self.Grid.addWidget(QLabel("<b>Is Home?</b>", self), 0, 0, Qt.AlignHCenter)
    self.Grid.addWidget(QLabel("<b>Name</b>", self), 0, 1, Qt.AlignHCenter)
    self.Grid.addWidget(QLabel("<b>Chore</b>", self), 0, 2, Qt.AlignHCenter)
    self.Grid.addWidget(QLabel("<b>Date completion</b>", self), 0, 3, Qt.AlignHCenter)
    self.Grid.addWidget(QLabel("<b>Name completion</b>", self), 0, 4, Qt.AlignHCenter)

    for i in range(len(self.DataHandlerObject.ConfigData['participants'])):
      for j in range(5):
        self.Grid.addWidget(QLabel(self), i+1, j, Qt.AlignHCenter)

    self.Grid.addWidget(QLabel('<b>Other</b>', self), len(self.DataHandlerObject.ConfigData['participants'])+1, 0, 1, 5, Qt.AlignHCenter)

    for i in range(2):
      self.Grid.addWidget(QLabel('(not yet set)',self), len(self.DataHandlerObject.ConfigData['participants'])+2+i, 2, Qt.AlignHCenter)

    dummy = QWidget()
    dummy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.Grid.addWidget(dummy,99,0)

  def Reset(self):
    self.NormalChoresInfo = []
    self.OtherChoresInfo = []
    self.DataHandlerObject.TempClearChores()
    auuids = self.DataHandlerObject.TempAddParticipants()
    for pid, name in self.DataHandlerObject.SortedParticipantsList:
      self.NormalChoresInfo.append({'personuuid' : pid, 'auuid' : auuids[pid]})
    del auuids
    self.Update()

  def LoadTempAssignment(self):
    auuids = {}
    self.NormalChoresInfo = []
    for ament in self.DataHandlerObject.TempWeekAsignment['normal']:
      auuids[self.DataHandlerObject.TempWeekAsignment['normal'][ament]['personuuid']] = self.DataHandlerObject.TempWeekAsignment['normal'][ament]['uuid']

    for pid, name in self.DataHandlerObject.SortedParticipantsList:
      self.NormalChoresInfo.append({'personuuid' : pid, 'auuid' : auuids[pid]})
    del auuids
    self.Update()

  def Update(self):
    for i, cinfo in enumerate(self.NormalChoresInfo):
      self.Grid.itemAtPosition(i+1, 0).widget().setText('Yes' if self.DataHandlerObject.GetItemKey('participants', cinfo['personuuid'], 'athome') else 'No')
      self.Grid.itemAtPosition(i+1, 1).widget().setText(self.DataHandlerObject.GetItemKey('participants', cinfo['personuuid'], 'name'))
      cuuid = self.DataHandlerObject.TempWeekAsignment['normal'][cinfo['auuid']]['choreuuid']
      self.Grid.itemAtPosition(i+1, 2).widget().setText('(not yet set)' if cuuid == '' else self.DataHandlerObject.GetItemKey('chores', cuuid, 'name'))

  def SetChore(self, pindex, cindex):
    self.DataHandlerObject.TempEditChore('normal', {'uuid' : self.NormalChoresInfo[pindex]['auuid'], 'choreuuid' : self.DataHandlerObject.SortedChoresList[cindex][0]})
    self.Update()

  def PermuteChores(self):
    temp = self.NormalChoresInfo[0]['auuid']
    for i in range(len(self.DataHandlerObject.SortedParticipantsList)-1):
      self.NormalChoresInfo[i]['auuid'] = self.NormalChoresInfo[i+1]['auuid']
    self.NormalChoresInfo[-1]['auuid'] = temp
    self.Update()

  def SaveTemp(self):
    self.DataHandlerObject.SaveAssignment(self.parent().SelectedDate)
    self.parent().Update()

  def SaveToFile(self):
    self.DataHandlerObject.TempSaveToTex(self.parent().SelectedDate, self.NormalChoresInfo)

class AssignmentsWidget(QWidget):
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
    self.Grid.addWidget(QLabel("<b>Year:</b>", self), 0, 0, 1, 1, Qt.AlignRight)
    self.LineEditCurrentYear = QLineEdit(self)
    self.LineEditCurrentYear.setAlignment(Qt.AlignHCenter)
    self.LineEditCurrentYear.setValidator(QIntValidator())
    self.Grid.addWidget(self.LineEditCurrentYear, 0, 1, 1, 1, Qt.AlignLeft)

    self.Grid.addWidget(QLabel("<b>Week:</b>", self), 0, 2, 1, 1, Qt.AlignRight)
    self.LineEditCurrentWeek = QLineEdit(self)
    self.LineEditCurrentWeek.setAlignment(Qt.AlignHCenter)
    self.LineEditCurrentWeek.setValidator(QIntValidator())
    self.Grid.addWidget(self.LineEditCurrentWeek, 0, 3, 1, 1, Qt.AlignLeft)

    self.LabelWeekDays = QLabel(self)
    self.Grid.addWidget(self.LabelWeekDays, 0, 4, 1, 2, Qt.AlignHCenter)

    self.FrameTable = FrameChoresTable(self.DataHandlerObject, self)
    self.Grid.addWidget(self.FrameTable, 1, 0, 1, 10, Qt.AlignHCenter)

    bchange = QPushButton("Change week")
    bchange.clicked.connect(self.ChangeWeek)
    self.Grid.addWidget(bchange, 2, 0, 1, 1, Qt.AlignHCenter)

    bprev = QPushButton("Prev week")
    bprev.clicked.connect(self.ChangeWeekPrev)
    self.Grid.addWidget(bprev, 2, 1, 1, 1, Qt.AlignHCenter)

    bcurrent = QPushButton("Current week")
    bcurrent.clicked.connect(self.ChangeWeekNow)
    self.Grid.addWidget(bcurrent, 2, 2, 1, 1, Qt.AlignHCenter)

    bnext = QPushButton("Next week")
    bnext.clicked.connect(self.ChangeWeekNext)
    self.Grid.addWidget(bnext, 2, 3, 1, 1, Qt.AlignHCenter)

    bsave = QPushButton('Save', self)
    bsave.clicked.connect(self.FrameTable.SaveTemp)
    self.Grid.addWidget(bsave, 2, 4, 1, 1, Qt.AlignHCenter)

    bsavefile = QPushButton('Save to tex', self)
    bsavefile.clicked.connect(self.FrameTable.SaveToFile)
    self.Grid.addWidget(bsavefile, 2, 5, 1, 1, Qt.AlignHCenter)

    self.Grid.addWidget(QLabel('<b>Manual assignment</b>', self), 3, 0, Qt.AlignHCenter)
    self.Grid.addWidget(QLabel('Person: ', self), 3, 1, Qt.AlignRight)

    self.CBoxMAPerson = QComboBox(self)
    self.MASelected = [0, 0]
    self.CBoxMAPerson.currentIndexChanged.connect(lambda i: self.SetSelectedCBox(0, i))
    self.Grid.addWidget(self.CBoxMAPerson, 3, 2, Qt.AlignLeft)

    self.Grid.addWidget(QLabel('Chore: ', self), 3, 3, Qt.AlignRight)

    self.CBoxMAChore = QComboBox(self)
    self.CBoxMAChore.currentIndexChanged.connect(lambda i: self.SetSelectedCBox(1, i))
    self.Grid.addWidget(self.CBoxMAChore, 3, 4, Qt.AlignLeft)

    bmanualadd = QPushButton('Set', self)
    bmanualadd.clicked.connect(self.SetChore)
    self.Grid.addWidget(bmanualadd, 3, 5, Qt.AlignHCenter)

    self.ChangeWeekNow()
    for pid, name in self.DataHandlerObject.SortedParticipantsList:
      self.CBoxMAPerson.addItem(name)

    for cid, name in self.DataHandlerObject.SortedChoresList:
      self.CBoxMAChore.addItem('%s (%d weeks ago, freq: %d weeks)' % (name, self.DataHandlerObject.GetWeekDifference(self.SelectedDate, cid), self.DataHandlerObject.GetItemKey('chores', cid, 'freq')))

    self.Grid.addWidget(QLabel('<b>Automatic assignment</b>', self), 4, 0, Qt.AlignHCenter)

    bauto1 = QPushButton('Load previous week', self)
    bauto1.clicked.connect(self.LoadPreviousWeek)
    self.Grid.addWidget(bauto1, 4, 1, 1, 1, Qt.AlignHCenter)

    bauto2 = QPushButton('Permute', self)
    bauto2.clicked.connect(self.FrameTable.PermuteChores)
    self.Grid.addWidget(bauto2, 4, 2, 1, 1, Qt.AlignHCenter)

    bauto3 = QPushButton('Remove completed', self)
    bauto3.clicked.connect(self.RemoveCompleted)
    self.Grid.addWidget(bauto3, 4, 3, 1, 1, Qt.AlignHCenter)

    bauto4 = QPushButton('Assign new', self)
    bauto4.clicked.connect(self.AssignNewChores)
    self.Grid.addWidget(bauto4, 4, 4, 1, 1, Qt.AlignHCenter)

  def ChangeWeek(self):
    self.SelectedYear, self.SelectedWeek = int(self.LineEditCurrentYear.text()), int(self.LineEditCurrentWeek.text())
    self.SelectedDate = datetime.datetime.strptime('%d-W%d-1' % (self.SelectedYear, self.SelectedWeek), "%Y-W%W-%w").date()

    self.SelectedYear, self.SelectedWeek = self.SelectedDate.isocalendar()[:2]

    self.LabelWeekDays.setText("<b>From</b> %s <b>to</b> %s" % (datetime.datetime.strptime('%d-W%d-1' % (self.SelectedYear, self.SelectedWeek), "%Y-W%W-%w").date(), datetime.datetime.strptime('%d-W%d-0' % (self.SelectedYear, self.SelectedWeek), "%Y-W%W-%w").date()))

    if self.DataHandlerObject.LoadAssignment(self.SelectedDate):
      self.FrameTable.LoadTempAssignment()
    else:
      self.FrameTable.Reset()

    self.Update()

  def ChangeWeekPrev(self):
    self.LineEditCurrentWeek.setText(str(self.SelectedWeek-1))
    self.ChangeWeek()
    self.LineEditCurrentYear.setText(str(self.SelectedYear))
    self.LineEditCurrentWeek.setText(str(self.SelectedWeek))

  def ChangeWeekNext(self):
    self.LineEditCurrentWeek.setText(str(self.SelectedWeek+1))
    self.ChangeWeek()
    self.LineEditCurrentYear.setText(str(self.SelectedYear))
    self.LineEditCurrentWeek.setText(str(self.SelectedWeek))

  def ChangeWeekNow(self):
    self.SelectedYear, self.SelectedWeek = datetime.date.today().isocalendar()[:2]
    self.LineEditCurrentYear.setText(str(self.SelectedYear))
    self.LineEditCurrentWeek.setText(str(self.SelectedWeek))
    self.ChangeWeek()

  def SetSelectedCBox(self, opt, index):
    self.MASelected[opt] = index

  def SetChore(self):
    self.FrameTable.SetChore(*self.MASelected)

  def LoadPreviousWeek(self):
    if self.DataHandlerObject.LoadAssignment(self.SelectedDate - datetime.timedelta(weeks=1)):
      self.FrameTable.LoadTempAssignment()
    else:
      self.parent().parent().parent().parent().statusBar().showMessage('Previous week data not found.', 5000)

  def RemoveCompleted(self):
    self.DataHandlerObject.TempRemoveCompleted()
    self.FrameTable.Update()

  def AssignNewChores(self):
    self.DataHandlerObject.TempAssignNewChores(self.SelectedDate)
    self.FrameTable.Update()

  def Update(self):
    self.FrameTable.Update()

    for i, (pid, name) in enumerate(self.DataHandlerObject.SortedParticipantsList):
      self.CBoxMAPerson.setItemText(i, name)

    for i, (cid, name) in enumerate(self.DataHandlerObject.SortedChoresList):
      self.CBoxMAChore.setItemText(i, '%s (%d weeks ago, freq: %d weeks)' % (name, self.DataHandlerObject.GetWeekDifference(self.SelectedDate, cid), self.DataHandlerObject.GetItemKey('chores', cid, 'freq')))
