# -*- coding: utf8 -*-
import functools

from datahandler import *
from .CompletionDialog import *
from .OtherChoresDialog import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

class AdvancedInfoDialog(QDialog):
  def __init__(self, dho, key, auuid, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho
    self.auuid = auuid
    self.key = key

    self.setWindowTitle('Advanced information')
    self.Grid = QGridLayout()
    self.Grid.setSpacing(10)
    self.setLayout(self.Grid)

    self.Init()

  def Init(self):
    for i, key in enumerate(self.DataHandlerObject.TempWeekAsignment[self.key][self.auuid]):
      self.Grid.addWidget(QLabel('<b>%s:</b>' % key, self), i, 0, 1, 1, Qt.AlignRight)
      self.Grid.addWidget(QLabel(str(self.DataHandlerObject.TempWeekAsignment[self.key][self.auuid][key]), self), i, 1, 1, 1, Qt.AlignLeft)

class FrameChoresTable(QFrame):
  def __init__(self, dho, parent):
    super().__init__(parent)
    self.DataHandlerObject = dho

    self.setFrameStyle(QFrame.Plain | QFrame.StyledPanel)
    self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.Grid = QGridLayout()
    self.Grid.setSpacing(10)
    self.setLayout(self.Grid)

    self.OtherLabelIndex = len(self.DataHandlerObject.ConfigData['participants'])+1

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

      bmore = QPushButton('More', self)
      bmore.clicked.connect(functools.partial(self.ShowMoreInfoDiag, 'normal', i))
      self.Grid.addWidget(bmore, i+1, 6, Qt.AlignHCenter)

    self.OtherChoresWidgets = []

    dummy = QWidget()
    dummy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    self.Grid.addWidget(dummy,99,0)

  def ShowMoreInfoDiag(self, key, index):
    AdvancedInfoDialog(self.DataHandlerObject, key, self.ChoresInfo['normal'][index]['auuid'], self).show()

  def Reset(self):
    self.ChoresInfo = {'normal':[]}
    self.DataHandlerObject.TempClearChores()
    auuids = self.DataHandlerObject.TempAddParticipants()

    for pid, name in self.DataHandlerObject.SortedParticipantsList:
      self.ChoresInfo['normal'].append({'personuuid' : pid, 'auuid' : auuids[pid]})

    del auuids
    self.Update()

  def LoadTempAssignment(self):
    auuids = {}
    self.ChoresInfo = {'normal':[]}

    for ament in self.DataHandlerObject.TempWeekAsignment['normal']:
      auuids[self.DataHandlerObject.TempWeekAsignment['normal'][ament]['personuuid']] = self.DataHandlerObject.TempWeekAsignment['normal'][ament]['uuid']

    for pid, name in self.DataHandlerObject.SortedParticipantsList:
      self.ChoresInfo['normal'].append({'personuuid' : pid, 'auuid' : auuids[pid]})

    del auuids
    self.Update()

  def Update(self):
    for i, cinfo in enumerate(self.ChoresInfo['normal']):
      self.Grid.itemAtPosition(i+1, 0).widget().setText('Yes' if self.DataHandlerObject.TempWeekAsignment['normal'][cinfo['auuid']]['home'] else 'No')

      self.Grid.itemAtPosition(i+1, 1).widget().setText(self.DataHandlerObject.GetItemKey('participants', cinfo['personuuid'], 'name'))

      cuuid = self.DataHandlerObject.TempWeekAsignment['normal'][cinfo['auuid']]['choreuuid']
      self.Grid.itemAtPosition(i+1, 2).widget().setText('(not yet set)' if cuuid == '' else self.DataHandlerObject.GetItemKey('chores', cuuid, 'name'))

      dcomp = self.DataHandlerObject.TempWeekAsignment['normal'][cinfo['auuid']]['datecomp']
      if len(dcomp):
        self.Grid.itemAtPosition(i+1, 3).widget().setText('%s' % datetime.date(*dcomp))
        self.Grid.itemAtPosition(i+1, 4).widget().setText(', '.join([self.DataHandlerObject.GetItemKey('participants', uuid, 'name') for uuid in self.DataHandlerObject.TempWeekAsignment['normal'][cinfo['auuid']]['puuidcomp']]))
      else:
        self.Grid.itemAtPosition(i+1, 3).widget().setText('')
        self.Grid.itemAtPosition(i+1, 4).widget().setText('')

    for wlist in self.OtherChoresWidgets:
      for w in wlist:
        w.setHidden(True)

    for i, auuid in enumerate(self.DataHandlerObject.TempWeekAsignment['other']):
      if self.Grid.itemAtPosition(self.OtherLabelIndex+i, 2) == None:
        self.OtherChoresWidgets.append([QLabel(self), QLabel(self), QLabel(self), QLabel(self)])
        for col, widget in enumerate(self.OtherChoresWidgets[-1]):
          self.Grid.addWidget(widget, self.OtherLabelIndex+i, col+1, Qt.AlignHCenter)
      else:
        for col in range(1, 5):
          self.Grid.itemAtPosition(self.OtherLabelIndex+i, col).widget().setHidden(False)

      self.Grid.itemAtPosition(self.OtherLabelIndex+i, 1).widget().setText('(anyone)')

      cuuid = self.DataHandlerObject.TempWeekAsignment['other'][auuid]['choreuuid']
      self.Grid.itemAtPosition(self.OtherLabelIndex+i, 2).widget().setText(self.DataHandlerObject.GetItemKey('chores', cuuid, 'name'))

      dcomp = self.DataHandlerObject.TempWeekAsignment['other'][auuid]['datecomp']
      if len(dcomp):
        self.Grid.itemAtPosition(self.OtherLabelIndex+i, 3).widget().setText('%s' % datetime.date(*dcomp))
        self.Grid.itemAtPosition(self.OtherLabelIndex+i, 4).widget().setText(', '.join([self.DataHandlerObject.GetItemKey('participants', uuid, 'name') for uuid in self.DataHandlerObject.TempWeekAsignment['other'][auuid]['puuidcomp']]))
      else:
        self.Grid.itemAtPosition(self.OtherLabelIndex+i, 3).widget().setText('')
        self.Grid.itemAtPosition(self.OtherLabelIndex+i, 4).widget().setText('')

  def SetChore(self, pindex, cindex):
    self.DataHandlerObject.TempEditChore('normal', {'uuid' : self.ChoresInfo['normal'][pindex]['auuid'], 'choreuuid' : self.DataHandlerObject.SortedChoresList[cindex][0]})
    self.Update()

  def PermuteChores(self):
    temp = self.DataHandlerObject.TempWeekAsignment['normal'][self.ChoresInfo['normal'][0]['auuid']]['choreuuid']
    for i in range(len(self.DataHandlerObject.SortedParticipantsList)-1):
      self.DataHandlerObject.TempWeekAsignment['normal'][self.ChoresInfo['normal'][i]['auuid']]['choreuuid'] = self.DataHandlerObject.TempWeekAsignment['normal'][self.ChoresInfo['normal'][i+1]['auuid']]['choreuuid']
    self.DataHandlerObject.TempWeekAsignment['normal'][self.ChoresInfo['normal'][-1]['auuid']]['choreuuid'] = temp
    self.LoadTempAssignment()

  def SaveTemp(self):
    self.DataHandlerObject.SaveAssignment(self.parent().SelectedDate)
    self.parent().Update()

  def SaveToFile(self):
    self.DataHandlerObject.TempSaveToTex(self.parent().SelectedDate, self.ChoresInfo['normal'])

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
    self.Grid.addWidget(self.CBoxMAPerson, 3, 2, Qt.AlignLeft)

    self.Grid.addWidget(QLabel('Chore: ', self), 3, 3, Qt.AlignRight)

    self.CBoxMAChore = QComboBox(self)
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

    self.Grid.addWidget(QLabel('<b>More:</b>', self), 5, 0, Qt.AlignHCenter)

    bcomp1 = QPushButton('Open completion dialog', self)
    bcomp1.clicked.connect(self.OpenCompletion)
    self.Grid.addWidget(bcomp1, 5, 1, 1, 1, Qt.AlignHCenter)

    bcomp1 = QPushButton('Open other chores dialog', self)
    bcomp1.clicked.connect(self.OpenOtherChores)
    self.Grid.addWidget(bcomp1, 5, 2, 1, 1, Qt.AlignHCenter)

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
    self.FrameTable.SetChore(self.CBoxMAPerson.currentIndex(), self.CBoxMAChore.currentIndex())

  def LoadPreviousWeek(self):
    if self.DataHandlerObject.LoadAsNewAssignment(self.SelectedDate - datetime.timedelta(weeks=1)):

      self.FrameTable.LoadTempAssignment()
    else:
      self.parent().parent().parent().parent().statusBar().showMessage('Previous week data not found.', 5000)

  def RemoveCompleted(self):
    self.DataHandlerObject.TempRemoveCompleted()
    self.FrameTable.Update()

  def AssignNewChores(self):
    self.DataHandlerObject.TempAssignNewChores(self.SelectedDate)
    self.FrameTable.Update()

  def OpenCompletion(self):
    CompletionDialog(self.DataHandlerObject, self).exec()
    self.FrameTable.Update()

  def OpenOtherChores(self):
    OtherChoresDialog(self.DataHandlerObject, self.SelectedDate, self).exec()
    self.FrameTable.Update()

  def Update(self):
    self.FrameTable.Update()

    for i, (pid, name) in enumerate(self.DataHandlerObject.SortedParticipantsList):
      self.CBoxMAPerson.setItemText(i, name)

    for i, (cid, name) in enumerate(self.DataHandlerObject.SortedChoresList):
      self.CBoxMAChore.setItemText(i, '%s (%d weeks ago, freq: %d weeks)' % (name, self.DataHandlerObject.GetWeekDifference(self.SelectedDate, cid), self.DataHandlerObject.GetItemKey('chores', cid, 'freq')))
