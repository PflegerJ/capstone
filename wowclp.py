#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
World of Warcraft, Combat Log Parser
---------

Copyright (c) 2013 Masayoshi Mizutani <mizutani@sfc.wide.ad.jp>
All rights reserved.
 *
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

-----------
Reference: http://www.wowwiki.com/API_COMBAT_LOG_EVENT
'''

import shlex
import time
import datetime

def resolv_power_type(pt):
    pt_map = {
        -2: 'health',
        0: 'mana',
        1: 'rage',
        2: 'focus',
        3: 'energy',
        4: 'pet happiness',
        5: 'runes',
        6: 'runic power'
    }
    return pt_map.get(pt)

def parse_unit_flag(flag):
    if isinstance(flag, str): f = int(flag, 0)
    else: f = flag

    res = []
    if f == 0: return res

    flag_map = {
        0x00004000: 'TYPE_OBJECT',
        0x00002000: 'TYPE_GUARDIAN',
        0x00001000: 'TYPE_PET',
        0x00000800: 'TYPE_NPC',
        0x00000400: 'TYPE_PLAYER',
        0x00000200: 'CONTROL_NPC',
        0x00000100: 'CONTROL_PLAYER',
        0x00000040: 'REACTION_HOSTILE',
        0x00000020: 'REACTION_NEUTRAL',
        0x00000010: 'REACTION_FRIENDLY',
        0x00000008: 'AFFILIATION_OUTSIDER',
        0x00000004: 'AFFILIATION_RAID',
        0x00000002: 'AFFILIATION_PARTY',
        0x00000001: 'AFFILIATION_MINE',
        0x08000000: 'RAIDTARGET8',
        0x04000000: 'RAIDTARGET7',
        0x02000000: 'RAIDTARGET6',
        0x01000000: 'RAIDTARGET5',
        0x00800000: 'RAIDTARGET4',
        0x00400000: 'RAIDTARGET3',
        0x00200000: 'RAIDTARGET2',
        0x00100000: 'RAIDTARGET1',
        0x00080000: 'MAINASSIST',
        0x00040000: 'MAINTANK',
        0x00020000: 'FOCUS',
        0x00010000: 'TARGET',
    }

    for (k, v) in iter(flag_map.items()):
        if (f & k) > 0: res.append(v)

    # print f, '->', repr(res)
    return res

def parse_school_flag(school):
    s = int(school, 0) if isinstance(school, str) else school
    
    res = []
    school_map = {
        0x1: 'Physical',
        0x2: 'Holy',
        0x4: 'Fire',
        0x8: 'Nature',
        0x10: 'Frost',
        0x20: 'Shadow',
        0x40: 'Arcane',
    }

    for (k, v) in iter(school_map.items()):
        if (s & k) > 0: res.append(v)

    return res


'''
---------------------------------------------------------
Prefix Parser Set
---------------------------------------------------------
'''

class SpellParser:
    def __init__(self): pass
    def parse(self, cols):
        return ({
            'spellId': cols[0],
            'spellName': cols[1],
            #'spellSchool': parse_school_flag(cols[2])
        }, cols[3:])

class EnvParser:
    def __init__(self): pass
    def parse(self, cols):
        return ({
            'environmentalType': cols[0]
        }, cols[1:])

class SwingParser:
    def __init__(self): pass
    def parse(self, cols): return ({}, cols)


'''
---------------------------------------------------------
Suffix Parser Set
---------------------------------------------------------
'''

class DamageParser:        
    def __init__(self): pass
    def parse(self, cols):
        cols = cols[8:]
        return {
            'amount': float(cols[8]),
            #'overkill': cols[1],
            #'school': parse_school_flag(cols[2]),
            'resisted': float(cols[3]),
            'blocked': float(cols[4]),
            'absorbed': float(cols[5]),
            #'critical': (cols[6] != 'nil'),
            #'glancing': (cols[7] != 'nil'),
            #'crushing': (cols[8] != 'nil'),
        }

class AbsorbedParser:
    def __init__(self): pass
    def parse(self, cols):
        obj = {
            'blah': -1
        }

        return obj

class MissParser:
    def __init__(self): pass
    def parse(self, cols):
        obj = {
            'missType': cols[0]
        }
        if len(cols) > 1: obj['isOffHand'] = cols[1]
        if len(cols) > 2: obj['amountMissed'] = int(cols[2])
        return obj

class HealParser:
    def __init__(self): pass
    def parse(self, cols):
        cols = cols[8:]
        return {
            'amount': int(cols[9]),
            'overhealing': int(cols[10]),
            'absorbed': int(cols[11]),
            'critical': (cols[12] != 'nil'),
        }

class EnergizeParser:
    def __init__(self): pass
    def parse(self, cols):
        cols = cols[8:]
        return {
            'amount': int(cols[0]),
            'powerType': resolv_power_type(cols[1]),
        }

class DrainParser:
    def __init__(self): pass
    def parse(self, cols):
        if len(cols) != 3: 
            print(cols)
        return {
            'amount': int(cols[0]),
            'powerType': resolv_power_type(cols[1]),
            'extraAmount': int(cols[2]),
        }

class LeechParser:
    def __init__(self): pass
    def parse(self, cols):
        if len(cols) != 3: 
            print(cols)
        return {
            'amount': int(cols[0]),
            'powerType': resolv_power_type(cols[1]),
            'extraAmount': int(cols[2]),
        }

class SpellBlockParser:
    def __init__(self): pass
    def parse(self, cols):
        if len(cols) != 3 and len(cols) != 4: 
            print(cols)
        obj = {
            'extraSpellID': cols[0],
            'extraSpellName': cols[1],
            #'extraSchool': parse_school_flag(cols[2]),
        }
        if len(cols) == 4: obj['auraType'] = cols[3]
        return obj

class ExtraAttackParser:
    def __init__(self): pass
    def parse(self, cols):
        if len(cols) != 1: 
            print(cols)
        return {
            'amount': int(cols[0])
        }

class AuraParser:
    def __init__(self): pass
    def parse(self, cols):
        if len(cols) > 4:
            print(self.raw)
            print(cols)

        obj = {
            'auraType': cols[0],
        }
        # 'auraSchool': cols[1],
        # 'auraType': cols[2],

        if len(cols) >= 2: obj['amount'] = int(cols[1])
        if len(cols) >= 3: obj['auraExtra1'] = cols[2] # Not sure this column 
        if len(cols) >= 4: obj['auraExtra2'] = cols[3] # Not sure this column 
        return obj

class AuraDoseParser:
    def __init__(self): pass
    def parse(self, cols):
        obj = {
            'auraType': cols[0],
        }
        if len(cols) == 2: obj['powerType'] = resolv_power_type(cols[1]) 
        return obj

class AuraBrokenParser:
    def __init__(self): pass
    def parse(self, cols):
        if len(cols) != 4: 
            print(cols)
        return {
            'extraSpellID': cols[0],
            'extraSpellName': cols[1],
            #'extraSchool': parse_school_flag(cols[2]),
            'auraType': cols[3],
        }

class CastFailedParser:
    def __init__(self): pass
    def parse(self, cols):
        if len(cols) != 1: 
            print(cols)
        return {
            'failedType': cols[0],
        }

'''
---------------------------------------------------------
Special Event Parser Set
---------------------------------------------------------
'''

class EnchantParser:
    def __init__(self): pass
    def parse(self, cols):
        return ({
            'spellName': cols[0],
            'itemID': cols[1],
            'itemName': cols[2],
        }, cols)

class EncountParser:
    def __init__(self): pass
    def parse(self, cols):
        obj = {
            'encounterID': cols[0],
            'encounterName': cols[1],
            'difficultyID': cols[2],
            'groupSize': cols[3],
        }
        if len(cols) == 5: obj['success'] = (cols[4] == '1')
        return obj

class  CombatantParser:
    def __init__(self): pass
    def parse(self, cols):
        obj = {
            "a": -1
        }
        return obj

class VoidParser:
    def __init__(self): pass
    def parse(self, cols): return ({}, cols)

class VoidSuffixParser:
    def __init__(self): pass
    def parse(self, cols): return {}
    



class Parser:
    def __init__(self):
        self.ev_prefix = {
            'SWING': SwingParser(),
            'SPELL_BUILDING': SpellParser(),
            'SPELL_PERIODIC': SpellParser(),
            'SPELL': SpellParser(),
            'RANGE': SpellParser(),
            'ENVIRONMENTAL': EnvParser(),
        }
        self.ev_suffix = {
            '_DAMAGE': DamageParser(),
            '_ABSORBED': AbsorbedParser(),
            '_DAMAGE_LANDED': DamageParser(),
            '_MISSED': MissParser(),
            '_HEAL': HealParser(),
            '_ENERGIZE': EnergizeParser(),
            '_DRAIN': DrainParser(),
            '_LEECH': LeechParser(),
            '_INTERRUPT': SpellBlockParser(),
            '_DISPEL': SpellBlockParser(),
            '_DISPEL_FAILED': SpellBlockParser(),
            '_STOLEN': SpellBlockParser(),
            '_EXTRA_ATTACKS': ExtraAttackParser(),
            '_AURA_APPLIED': AuraParser(),
            '_AURA_REMOVED': AuraParser(),
            '_AURA_APPLIED_DOSE': AuraDoseParser(),
            '_AURA_REMOVED_DOSE': AuraDoseParser(),
            '_AURA_REFRESH': AuraDoseParser(),
            '_AURA_BROKEN': AuraParser(),
            '_AURA_BROKEN_SPELL': AuraBrokenParser(),
            '_CAST_START': VoidSuffixParser(),
            '_CAST_SUCCESS': VoidSuffixParser(),
            '_CAST_FAILED': CastFailedParser(),
            '_INSTAKILL': VoidSuffixParser(),
            '_DURABILITY_DAMAGE': VoidSuffixParser(),
            '_DURABILITY_DAMAGE_ALL': VoidSuffixParser(),
            '_CREATE': VoidSuffixParser(),
            '_SUMMON': VoidSuffixParser(),
            '_RESURRECT': VoidSuffixParser(),
        }
        self.sp_event = {
            'DAMAGE_SHIELD': (SpellParser(), DamageParser()),
            'DAMAGE_SPLIT': (SpellParser(), DamageParser()),
            'DAMAGE_SHIELD_MISSED': (SpellParser(), MissParser()),
            'ENCHANT_APPLIED': (EnchantParser(), VoidSuffixParser()),
            'ENCHANT_REMOVED': (EnchantParser(), VoidSuffixParser()),
            'PARTY_KILL': (VoidParser(), VoidSuffixParser()),
            'UNIT_DIED': (VoidParser(), VoidSuffixParser()),
            'UNIT_DESTROYED': (VoidParser(), VoidSuffixParser()),
        }
        self.enc_event = {
            'ENCOUNTER_START': EncountParser(),
            'ENCOUNTER_END': EncountParser(),
            'COMBATANT_INFO': CombatantParser()
        }


    def parse_line(self, line):
        terms = line.split(' ')
        if len(terms) < 4: raise Exception('invalid format, ' + line)

        # split timestamp
        s = '{2} {0[0]:02d}/{0[1]:02d} {1}'.format(list(map(int, terms[0].split('/'))), 
                                                   terms[1][:-4], 
                                                   datetime.datetime.today().year)
        d = datetime.datetime.strptime(s, '%Y %m/%d %H:%M:%S')
        ts = time.mktime(d.timetuple()) + float(terms[1][-4:])

        # split CSV data
        csv_txt = ' '.join(terms[3:]).strip()
        if csv_txt[0:5] == 'EMOTE':
            return {"a": -1}
        if csv_txt[0:11] == "SPELL_DRAIN":
            return {"a": -1}
        if csv_txt[0:10] == "COMBAT_LOG":
            return {"a": -1}
        splitter = shlex.shlex(csv_txt, posix=True)
        splitter.whitespace = ','
        splitter.whitespace_split = True
        cols = list(splitter)
        obj = self.parse_cols(ts, cols)

        '''
        if obj['event'] == 'SPELL_AURA_APPLIED': 
            print obj
            for i in range(len(cols)): print i, cols[i]
'''
        return obj


    def parse_cols(self, ts, cols):
        event = cols[0]

        if self.enc_event.get(event):
            obj = {
                'timestamp': ts,
                'event': event,
            }
            obj.update(self.enc_event[event].parse(cols[1:]))
            return obj

        if len(cols) < 8: 
            return {"a": -1}
            #raise Exception('invalid format, ' + repr(cols))
        obj = {'timestamp': ts,
               'event': event,
               'sourceGUID':   cols[1],
               'sourceName':   cols[2],
               'sourceFlags':  parse_unit_flag(cols[3]),
               'sourceFlags2': parse_unit_flag(cols[4]),
               'destGUID':   cols[5],
               'destName':   cols[6],
               'destFlags':  parse_unit_flag(cols[7]),
               'destFlags2': parse_unit_flag(cols[8])}

        prefix = ''
        suffix = ''
        prefix_psr = None
        suffix_psr = None

        matches = []
        for (k, p) in iter(self.ev_prefix.items()):
            if event.startswith(k): matches.append(k)

        if len(matches) > 0:
            prefix = max(matches, key=len)
            prefix_psr = self.ev_prefix[prefix]
            suffix = event[len(prefix):]
            suffix_psr = self.ev_suffix[suffix]
        else:
            for (k, psrs) in iter(self.sp_event.items()):
                if event == k:
                    (prefix_psr, suffix_psr) = psrs
                    break
                
        if prefix_psr is None or suffix_psr is None:
            raise Exception('Unknown event format, ' + repr(cols))

        (res, remain) = prefix_psr.parse(cols[9:])
        obj.update(res)
        suffix_psr.raw = cols
        obj.update(suffix_psr.parse(remain))

        # if obj['destName'] == 'Muret' and obj['event'] == 'SPELL_HEAL': 
        '''
        if obj['event'] == 'SPELL_DISPEL':
            print obj
        '''
        p = {"prefix": prefix}
        s = {"suffix": suffix}
        obj.update(p)
        obj.update(s)
        return obj

    def read_file(self, fname):
        for line in open(fname, 'r'):
            yield self.parse_line(line)
            




