# -*- coding: utf8 -*-
import json
import datetime
import uuid
import copy

class DataHandler:
  def __init__(self):
    self.ConfigFile = 'config/config.json'
    self.AssignmentsFile = 'config/assignments.json'
    self.ConfigData = {"chores":{},"participants":{}}
    self.AssignmentsData = {}

    self.TempWeekAsignment = {}

    self.NotFoundData = {'chores' : {"freq": -1, "priority": -1, "alast": "0001-W1", "timestamp": "(not found)", "name": "(not found)", "uuid": "(not found)", "atimes": -1}, 'participants' : {"cando": False, "uuid": "(not found)", "timestamp": "(not found)", "name": "(not found)", "athome": False}}

    try:
      config_file = open(self.ConfigFile, 'r')
      file_string = config_file.read()
      config_file.close()
      self.ConfigData.update(json.loads(file_string))
    except Exception as e:
      print("Error loading configuration file: %s" % e)
      self.UpdateConfigFile()

    self.GenerateSortedLists()

    try:
      assignments_file = open(self.AssignmentsFile, 'r')
      file_string = assignments_file.read()
      assignments_file.close()
      self.AssignmentsData.update(json.loads(file_string))
    except Exception as e:
      print("Error loading assignments file: %s" % e)
      self.UpdateAssignmentsFile()

  def GenerateSortedLists(self):
    self.SortedParticipantsList = [(pid, self.GetItemKey('participants', pid, 'name')) for pid in self.ConfigData['participants']]
    self.SortedParticipantsList.sort(key=lambda e: e[1].lower())
    self.SortedChoresList = [(pid, self.GetItemKey('chores', pid, 'name')) for pid in self.ConfigData['chores']]
    self.SortedChoresList.sort(key=lambda e: e[1].lower())

  def AddNewItem(self, key, new_data):
    new_data.update({"timestamp": str(datetime.datetime.now()), "uuid": str(uuid.uuid4())})
    self.ConfigData[key][new_data['uuid']] = new_data
    self.GenerateSortedLists()
    self.UpdateConfigFile()

  def EditItem(self, key, uuid, new_data):
    self.ConfigData[key][uuid].update(new_data)
    self.GenerateSortedLists()
    self.UpdateConfigFile()

  def RemoveItem(self, key, uuid):
    del self.ConfigData[key][uuid]
    self.GenerateSortedLists()
    self.UpdateConfigFile()

  def GetItem(self, key, uuid):
    try:
      return self.ConfigData[key][uuid]
    except Exception as e:
      return self.NotFoundData[key]

  def GetItemKey(self, key, uuid, itemkey):
    try:
      return self.ConfigData[key][uuid][itemkey]
    except Exception as e:
      return self.NotFoundData[key][itemkey]

  def GetWeekDifference(self, cdate, choreuuid):
    return int((cdate - datetime.datetime.strptime(self.GetItemKey('chores', choreuuid, 'alast') + '-1', "%Y-W%W-%w").date()).days / 7)

  def TempClearChores(self):
    del self.TempWeekAsignment
    self.TempWeekAsignment = { 'normal' : {}, 'other' : {} }

  def TempAddParticipants(self):
    uuids = {}
    for p in self.ConfigData['participants']:
      uuids[p] = self.TempAddChore('normal', '', p)
    return uuids

  def TempAddChore(self, key, cid = '', pid = ''):
    if key == 'normal':
      new_data = {"timestamp": str(datetime.datetime.now()), "uuid": str(uuid.uuid4()), 'personuuid' : pid, 'choreuuid' : cid, 'datecomp' : '', 'puuidcomp' : ''}
      self.TempWeekAsignment['normal'][new_data['uuid']] = new_data
    elif key == 'other' and cid != '':
      new_data = {"timestamp": str(datetime.datetime.now()), "uuid": str(uuid.uuid4()), 'choreuuid' : cid, 'datecomp' : '', 'puuidcomp' : ''}
      self.TempWeekAsignment['other'][new_data['uuid']] = new_data
    return new_data['uuid']

  def TempRemoveChore(self, key, uuid):
    del self.TempWeekAsignment[key][uuid]

  def TempEditChore(self, key, new_data):
    self.TempWeekAsignment[key][new_data['uuid']].update(new_data)

  def SaveAssignment(self, cdate):
    cdatestr = '%d-W%d' % cdate.isocalendar()[:2]

    if cdatestr in self.AssignmentsData:
      self.AssignmentsData[cdatastr].update(self.TempWeekAsignment)
    else:
      self.AssignmentsData[cdatastr] = self.TempWeekAsignment

    self.UpdateAssignmentsFile()

  def LoadAssignment(self, cdate):
    cdatestr = '%d-W%d' % cdate.isocalendar()[:2]

    if cdatestr in self.AssignmentsData:
      self.TempWeekAsignment = self.AssignmentsData[cdatastr]

  def UpdateConfigFile(self):
    try:
      config_file = open(self.ConfigFile, 'w+')
      json.dump(self.ConfigData, config_file)
      config_file.close()
    except Exception as e:
      print("Error saving configuration file: %s" % e)

  def UpdateAssignmentsFile(self):
    try:
      assignments_file = open(self.AssignmentsFile, 'w+')
      json.dump(self.AssignmentsData, assignments_file)
      assignments_file.close()
    except Exception as e:
      print("Error saving assignments file: %s" % e)
