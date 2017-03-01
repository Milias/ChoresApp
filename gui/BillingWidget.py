# -*- coding: utf8 -*-
import functools

from datahandler import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import json

class BillingWidget(QWidget):
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
    self.Grid.addWidget(QLabel('Choose date interval'), 0, 0, 0, 0, Qt.AlignHCenter)

  def Update(self):
    self.FrameTable.Update()
