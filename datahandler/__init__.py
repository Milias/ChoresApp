# -*- coding: utf8 -*-
import json
import datetime
import uuid
import copy
import re
import random

def tex_escape(text):
    '''
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    '''
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
    self.BillingFile = 'config/billing.json'
    self.DataTexFile = 'tex/data.tex'
    self.DateTexFile = 'tex/date.tex'
    self.BankTexFile = 'tex/bank_details.tex'

    self.ConfigData = { 'chores' : {}, 'participants' : {} }
    self.AssignmentsData = {}
    self.BillingData = { 'config' : {'recurring' : 0.0, 'bank_name' : '', 'acc_no' : '', 'acc_holder' : '', 'loc' : ''}, 'bills' : {}, 'group_bills' : {}, 'expenses' : {}, 'payments' : {} }

    self.TempWeekAsignment = {}

    self.NotFoundData = {
      'chores' :
        {'freq': -1, 'priority': -1, 'alast': '0001-W1', 'timestamp': '(not found)', 'name': '(not found)', 'uuid': '(not found)', 'atimes': -1, 'points': 0},
      'participants' :
        {'uuid': '(not found)', 'timestamp': '(not found)', 'name': '(not found)', 'home': False}
    }

    try:
      config_file = open(self.ConfigFile, 'r')
      file_string = config_file.read()
      config_file.close()
      self.ConfigData.update(json.loads(file_string))

    except Exception as e:
      print('Error loading configuration file: %s' % e)

    self.UpdateConfigFile()
    self.GenerateSortedLists()

    try:
      assignments_file = open(self.AssignmentsFile, 'r')
      file_string = assignments_file.read()
      assignments_file.close()
      self.AssignmentsData.update(json.loads(file_string))

    except Exception as e:
      print('Error loading assignments file: %s' % e)

    self.UpdateAssignmentsFile()

    try:
      billing_file = open(self.BillingFile, 'r')
      file_string = billing_file.read()
      billing_file.close()
      self.BillingData.update(json.loads(file_string))

    except Exception as e:
      print('Error loading billing file: %s' % e)

    self.UpdateBillingFile()

  def GenerateSortedLists(self):
    self.SortedParticipantsList = [(pid, self.GetItemKey('participants', pid, 'name')) for pid in self.ConfigData['participants']]
    self.SortedParticipantsList.sort(key=lambda e: e[1].lower())
    self.SortedChoresList = [(pid, self.GetItemKey('chores', pid, 'name')) for pid in self.ConfigData['chores']]
    self.SortedChoresList.sort(key=lambda e: e[1].lower())

  def AddNewItem(self, key, new_data):
    new_data.update({'timestamp': str(datetime.datetime.now()), 'uuid': str(uuid.uuid4())})
    self.ConfigData[key][new_data['uuid']] = new_data
    self.GenerateSortedLists()
    self.UpdateConfigFile()
    return new_data['uuid']

  def EditItem(self, key, uuid, new_data):
    try:
      self.ConfigData[key][uuid].update(new_data)
      self.GenerateSortedLists()
      self.UpdateConfigFile()
    except:
      return

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

  def BillingAddNewItem(self, key, new_data):
    new_data.update({'timestamp': str(datetime.datetime.now()), 'tuuid': str(uuid.uuid4())})
    self.BillingData[key][new_data['tuuid']] = new_data
    self.UpdateBillingFile()
    return new_data['tuuid']

  def BillingEditItem(self, key, uuid, new_data):
    self.BillingData[key][uuid].update(new_data)
    self.UpdateBillingFile()

  def BillingRemoveItem(self, key, uuid):
    del self.BillingData[key][uuid]
    self.UpdateBillingFile()

  def BillingGetItemsInRange(self, key, date0 = None, date1 = None):
    if date0 and date1:
      return [tuuid for tuuid in self.BillingData[key] if date0 <= datetime.date(*self.BillingData[key][tuuid]['date']) <= date1]
    elif date0 and date1 == None:
      return [tuuid for tuuid in self.BillingData[key] if date0 <= datetime.date(*self.BillingData[key][tuuid]['date'])]
    elif date0 == None and date1:
      return [tuuid for tuuid in self.BillingData[key] if datetime.date(*self.BillingData[key][tuuid]['date']) <= date1]
    else:
      return list(self.BillingData[key].keys())

  def ComputeDateFromWeek(self, str_date, day = 1):
    return datetime.datetime.strptime('%s-%d' % (str_date, day), '%Y-W%W-%w').date()

  def BillingGetChoresInRange(self, date0, date1):
    # chores_data[puuid] = reward
    chores_data = {}
    for (pid, name) in self.SortedParticipantsList:
      chores_data[pid] = 0.0

    for key in self.AssignmentsData:
      if date0 <= self.ComputeDateFromWeek(key) < date1:
        for auuid in self.AssignmentsData[key]['normal']:
          reward = self.GetItemKey('chores', self.AssignmentsData[key]['normal'][auuid]['choreuuid'], 'reward')

          chores_data[self.AssignmentsData[key]['normal'][auuid]['personuuid']] += reward * ( 1.0 if self.AssignmentsData[key]['normal'][auuid]['home'] else 0.0 )

          for pid in self.AssignmentsData[key]['normal'][auuid]['puuidcomp']:
            chores_data[pid] -= reward

        for auuid in self.AssignmentsData[key]['other']:
          reward = self.GetItemKey('chores', self.AssignmentsData[key]['other'][auuid]['choreuuid'], 'reward')

          for pid in self.AssignmentsData[key]['other'][auuid]['puuidcomp']:
            chores_data[pid] -= reward

    return chores_data

  def ComputeCurrentBalance(self, puuid):
    bills = sum([self.BillingData['bills'][key]['bill_data']['subtotal'] for key in self.BillingData['bills'] if self.BillingData['bills'][key]['puuid'] == puuid])
    payments = sum([self.BillingData['payments'][key]['amount'] for key in self.BillingData['payments'] if self.BillingData['payments'][key]['puuid'] == puuid])
    return bills - self.GetItemKey('participants', puuid, 'boffset') - payments

  def GetWeekDifference(self, cdate, choreuuid):
    return int((cdate - self.ComputeDateFromWeek(self.GetItemKey('chores', choreuuid, 'alast'))).days / 7)

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
      new_data = {'timestamp': str(datetime.datetime.now()), 'uuid': str(uuid.uuid4()), 'personuuid' : pid, 'choreuuid' : cid, 'datecomp' : [], 'puuidcomp' : [], 'home' : True}
      self.TempWeekAsignment['normal'][new_data['uuid']] = new_data
    elif key == 'other' and cid != '':
      uuidvar = self.TempCheckChore(cid, ('other',))
      if uuidvar: return uuidvar
      new_data = {'timestamp': str(datetime.datetime.now()), 'uuid': str(uuid.uuid4()), 'choreuuid' : cid, 'datecomp' : [], 'puuidcomp' : []}
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
        self.TempWeekAsignment['normal'][auuids[self.AssignmentsData[cdatestr]['normal'][uuid]['personuuid']]]['home'] = self.GetItemKey('participants', self.AssignmentsData[cdatestr]['normal'][uuid]['personuuid'], 'athome')
      return True

    return False

  def TempSaveToTex(self, cdate, adict):
    try:
      tex_file = open(self.DateTexFile, 'w+')
      tex_file.write('Week \\textbf{%s} -- From \\textbf{%s} to \\textbf{%s}' % (cdate.isocalendar()[1], self.ComputeDateFromWeek(datetime.datetime.strftime(cdate, '%Y-W%W'), 1), self.ComputeDateFromWeek(datetime.datetime.strftime(cdate, '%Y-W%W'), 0)))
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

  def BillingSaveToTex(self, gbuuid):
    try:
      tex_file = open(self.DateTexFile, 'w+')
      date_range = tuple([datetime.datetime.strftime(datetime.date(*d), '%Y-%m-%d') for d in self.BillingData['group_bills'][gbuuid]['date_range']])

      tex_file.write('Dates: \\textbf{%s} --- \\textbf{%s}' % date_range)

      tex_file.close()

      tex_file = open(self.DataTexFile, 'w+')
      tex_str = []

      sorted_bills = [(buuid, self.GetItemKey('participants', self.BillingData['bills'][buuid]['puuid'], 'name')) for buuid in self.BillingData['group_bills'][gbuuid]['buuids']]
      sorted_bills.sort(key=lambda e: e[1].lower())

      rec = self.BillingData['group_bills'][gbuuid]['group_bill_data']['recurring']
      ssc = self.BillingData['group_bills'][gbuuid]['group_bill_data']['shared_shopping_costs']

      for i, (buuid, name) in enumerate(sorted_bills):
        contribution = self.BillingData['bills'][buuid]['bill_data']['contribution']
        psc = self.BillingData['bills'][buuid]['bill_data']['personal_shopping_costs']
        chores = self.BillingData['bills'][buuid]['bill_data']['chores']
        subtotal = self.BillingData['bills'][buuid]['bill_data']['subtotal']
        balance = self.ComputeCurrentBalance(self.BillingData['bills'][buuid]['puuid'])

        tex_str.append('%s & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & \\emph{%.2f} \\\\ \\hline' % (tex_escape(name), rec, ssc, contribution, psc, chores, subtotal, balance))

      tex_file.write('\n'.join(tex_str))
      tex_file.close()

      tex_file = open(self.BankTexFile, 'w+')

      tex_str = '%s & %s & %s & %s \\\\ \\hline' % tuple([self.BillingData['config'][key] for key in self.BillingData['config'] if isinstance(self.BillingData['config'][key], str)])

      tex_file.write(tex_str)
      tex_file.close()

    except Exception as e:
      print('Error writing to data.tex: %s' % e)

  def UpdateConfigFile(self):
    try:
      config_file = open(self.ConfigFile, 'w+')
      json.dump(self.ConfigData, config_file)
      config_file.close()
    except Exception as e:
      print('Error saving configuration file: %s' % e)

  def UpdateAssignmentsFile(self):
    try:
      assignments_file = open(self.AssignmentsFile, 'w+')
      json.dump(self.AssignmentsData, assignments_file)
      assignments_file.close()
    except Exception as e:
      print('Error saving assignments file: %s' % e)

  def UpdateBillingFile(self):
    try:
      billing_file = open(self.BillingFile, 'w+')
      json.dump(self.BillingData, billing_file)
      billing_file.close()
    except Exception as e:
      print('Error saving assignments file: %s' % e)
