# -*- coding: utf8 -*-
import json
import datetime
import uuid
import copy
import re
import random

def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless',
        '>': r'\textgreater',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

class DataHandler:
  def __init__(self):
    self.ConfigFile = 'config/config.json'
    self.AssignmentsFile = 'config/assignments.json'
    self.DataTexFile = 'tex/data.tex'
    self.DateTexFile = 'tex/date.tex'
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
      new_data = {"timestamp": str(datetime.datetime.now()), "uuid": str(uuid.uuid4()), 'personuuid' : pid, 'choreuuid' : cid, 'datecomp' : [], 'puuidcomp' : []}
      self.TempWeekAsignment['normal'][new_data['uuid']] = new_data
    elif key == 'other' and cid != '':
      uuidvar = self.TempCheckChore(cid, ('other',))
      if uuidvar: return uuidvar
      new_data = {"timestamp": str(datetime.datetime.now()), "uuid": str(uuid.uuid4()), 'choreuuid' : cid, 'datecomp' : [], 'puuidcomp' : []}
      self.TempWeekAsignment['other'][new_data['uuid']] = new_data
    return new_data['uuid']

  def TempRemoveChore(self, key, uuid):
    del self.TempWeekAsignment[key][uuid]

  def TempEditChore(self, key, new_data):
    self.TempWeekAsignment[key][new_data['uuid']].update(new_data)

  def TempCheckChore(self, uuid, keys = ('normal', 'other')):
    for key in keys:
      for auuid in self.TempWeekAsignment[key]:
        if self.TempWeekAsignment[key][auuid]['choreuuid'] == uuid:
          return auuid
    return ''

  def TempRemoveCompleted(self):
    for key in self.TempWeekAsignment['normal']:
      if self.GetItemKey('chores', self.TempWeekAsignment['normal'][key]['choreuuid'], 'freq') > 1:
        self.TempWeekAsignment['normal'][key]['choreuuid'] = ''

  def TempAssignNewChores(self, cdate):
    assigned = [self.TempWeekAsignment[key1][key2]['choreuuid'] for key1 in self.TempWeekAsignment for key2 in self.TempWeekAsignment[key1] if self.TempWeekAsignment[key1][key2]['choreuuid'] != '']
    new_chores = [cid for cid in self.ConfigData['chores'] if self.GetWeekDifference(cdate, cid) >= self.GetItemKey('chores', cid, 'freq') and not cid in assigned]
    random.shuffle(new_chores)

    nassigned = 0
    for key in self.TempWeekAsignment:
      if len(new_chores) == nassigned: break
      for uuid in self.TempWeekAsignment[key]:
        if len(new_chores) == nassigned: break
        if self.TempWeekAsignment[key][uuid]['choreuuid'] == '':
          self.TempWeekAsignment[key][uuid]['choreuuid'] = new_chores[nassigned]
          nassigned += 1

  def SaveAssignment(self, cdate):
    cdatestr = '%d-W%d' % cdate.isocalendar()[:2]

    if cdatestr in self.AssignmentsData:
      self.AssignmentsData[cdatestr].update(self.TempWeekAsignment)
    else:
      self.AssignmentsData[cdatestr] = copy.deepcopy(self.TempWeekAsignment)

    for key in self.TempWeekAsignment:
      for uuid in self.TempWeekAsignment[key]:
        if self.TempWeekAsignment[key][uuid]['choreuuid'] == '': continue
        #if self.GetWeekDifference(cdate, self.TempWeekAsignment[key][uuid]['choreuuid']) > 0:
        self.EditItem('chores', self.TempWeekAsignment[key][uuid]['choreuuid'], {'alast' : '%d-W%d' % cdate.isocalendar()[:2]})

    self.UpdateAssignmentsFile()

  def LoadAssignment(self, cdate):
    cdatestr = '%d-W%d' % cdate.isocalendar()[:2]

    if cdatestr in self.AssignmentsData:
      del self.TempWeekAsignment
      self.TempWeekAsignment = copy.deepcopy(self.AssignmentsData[cdatestr])
      return True

    return False

  def LoadAsNewAssignment(self, cdate):
    cdatestr = '%d-W%d' % cdate.isocalendar()[:2]

    if cdatestr in self.AssignmentsData:
      self.TempClearChores()
      auuids = self.TempAddParticipants()

      for uuid in self.AssignmentsData[cdatestr]['normal']:
        self.TempWeekAsignment['normal'][auuids[self.AssignmentsData[cdatestr]['normal'][uuid]['personuuid']]]['choreuuid'] = self.AssignmentsData[cdatestr]['normal'][uuid]['choreuuid']
      return True

    return False

  def TempSaveToTex(self, cdate, adict):
    try:
      tex_file = open(self.DateTexFile, 'w+')
      tex_file.write('Week \\textbf{%s} -- From \\textbf{%s} to \\textbf{%s}' % (cdate.isocalendar()[1], datetime.datetime.strptime('%d-W%d-1' % cdate.isocalendar()[:2], "%Y-W%W-%w").date(), datetime.datetime.strptime('%d-W%d-0' % cdate.isocalendar()[:2], "%Y-W%W-%w").date()))
      tex_file.close()

      tex_file = open(self.DataTexFile, 'w+')
      tex_str = []

      for i, (uuid, name) in enumerate(self.SortedParticipantsList):
        tex_str.append('%s & %s & %s & \phantom{---------------} & \\\\[0.25cm] \\hline' % ('Yes' if self.GetItemKey('participants', uuid, 'athome') else 'No', tex_escape(name), tex_escape(self.GetItemKey('chores', self.TempWeekAsignment['normal'][adict[i]['auuid']]['choreuuid'], 'name'))))

      for auuid in self.TempWeekAsignment['other']:
        tex_str.append('& (anyone) & %s & \phantom{---------------} & \\\\[0.15cm] \\hline' %  tex_escape(self.GetItemKey('chores', self.TempWeekAsignment['other'][auuid]['choreuuid'], 'name')))

      for i in range(max(0, 3-len(self.TempWeekAsignment['other']))):
        tex_str.append('& & & \phantom{---------------} & \\\\[0.15cm] \\hline')

      tex_file.write('\n'.join(tex_str))
      tex_file.close()
    except Exception as e:
      print('Error writing to data.tex: %s' % e)

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
