import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import wowclp



def getAverage(data):
    total = 0
    for value in data:
        total = total + value
    
    return total / len(data)


def getInfoFromLog(filename, cut_off_time, boss_name):
    current_line = 392
    #fileName = "C:/Program Files (x86)/World of Warcraft/_classic_/Logs/WoWCombatLog-021523_182914.txt"
    file = open(filename, encoding="utf-8")
    #fileAsList = file.readlines()

    start_time = 0.0
    current_time = 0.0

    healing = 0


    psr = wowclp.Parser()
    i = 1

    damage_done = 0.0
    healing_amount = 0.0
    damage_taken = 0.0

    dps = []
    hps = []
    dtps = []

    dps_avg = []
    healing_avg = []
    dtps_avg = []

    encounter_started = False
    encounter_ended = False

    start_time = 0
    next_time = 0
    current_time = 0
    end_time = 0
    step_count = 0
    seconds_recorded = 0

    pies = 0
    swing = 0

    total_dmg_done = 0
    total_healing = 0
    total_dmg_taken = 0

    for line in file:
        if encounter_ended:
            break
        obj = psr.parse_line(line)
        if not "a" in obj:
            if encounter_started:
                if obj["event"] == "ENCOUNTER_END":
                    encounter_ended = True 
                    end_time = obj["timestamp"]
                else:
                    current_time = obj["timestamp"]          
                    if obj["suffix"] == "_HEAL":
                        if obj["destGUID"][0:6] == "Player":
                            healing_amount = healing_amount + obj['amount'] - obj['overhealing']
                            if healing_amount > 40000:
                                z = 2
                            total_healing = total_healing + obj['amount'] - obj['overhealing']
                        #print("line: " + str(i) + " " +  "source: " + obj["sourceName"] + " " + "target: " + obj["destName"] + " " + "spell: " + obj["spellName"] + " " + "amount: " + str(obj["amount"]))
                    elif obj["suffix"] == "_DAMAGE":
                        # determine target
                        if obj["destGUID"][0:6] == "Player":
                            damage_taken = damage_taken + obj["amount"]
                            total_dmg_taken = total_dmg_taken + obj["amount"]
                            if obj["destName"] == "Laidyofpies-Whitemane":
                                if obj['event'] == "SWING_DAMAGE":
                                    swing = swing + obj['amount']
                                pies = pies + obj["amount"]
                                #print("line: " + str(i) + " " +  "source: " + obj["sourceName"] + " " + "target: " + obj["destName"] + " " + "amount: " + str(obj["amount"]))

                        else:
                            damage_done = damage_done + obj["amount"]
                            total_dmg_done = total_dmg_done + obj["amount"]
                        z = 2

                if current_time > next_time:

                    dps.append(damage_done)
                    hps.append(healing_amount)             
                    dtps.append(damage_taken)

                    damage_done = 0
                    healing_amount = 0
                    damage_taken = 0

                    next_time = next_time + 1
                    step_count = step_count + 1

                    seconds_recorded = seconds_recorded + 1

                    if seconds_recorded == 239:
                        z = 2
                    if seconds_recorded >= cut_off_time:
                        encounter_ended = True      
            
            else:
                if obj["event"] == "ENCOUNTER_START":
                    if obj["encounterName"] == boss_name:
                        encounter_started = True
                        start_time = obj["timestamp"]
                        end_time = start_time + cut_off_time
                        next_time = start_time + 1
        

        # Combat start
            # grab time stamp

        # Combat End or time limit has passed

        # Damage
            # Damage to boss
            # Damage to player

        # Heal
        i = i + 1
        # 0.5 seconds have passed
    x4 = np.arange(0, len(dtps), 1)
    plt.plot(x4, dtps, color="yellow")
    #plt.show()
    #print("total dmg  done: " + str(total_dmg_done) + " " + "total healing: "+ str(total_healing) + " "+  "total dmg taken: " + str(total_dmg_taken) + " " + "pies: " + str(pies))
    return dps, hps, dtps

"""
    key = list(obj.values())
    if key[0] != -1:
        print("line: " + str(i) + " " + obj["event"])
    i = i + 1
"""

"""


print("total dmg  done: " + str(total_dmg_done) + " " + "total healing: "+ str(total_healing) + " "+  "total dmg taken: " + str(total_dmg_taken) + " " + "pies: " + str(pies))
#print(start_time)
#print(end_time)

df_dps = pd.read_csv("feb20DPS.csv")
df_hps = pd.read_csv("feb20HPS.csv")
df_dtps = pd.read_csv("feb20DTPS.csv")

df_dps = df_dps["damage"]
df_heal = df_hps["healing"]
df_dtps = df_dtps["damage_taken"]

x2 = np.arange(223.993, step=0.933)
#print(x2)
print(total_healing)
duration = end_time - start_time
#print(duration)
x1 = np.arange(0, len(hps), 1)
x3 = np.arange(0, len(dps), 1)
x4 = np.arange(0, len(dtps), 1)
x1 = x1
#print(x1)
#plt.plot(x1, hps, color="blue")
#plt.plot(x3, dps, color="green")
plt.plot(x4, dtps, color="yellow")
#plt.plot(x2, df_heal, color='red')
#plt.plot(x2, df_dps, color='purple')
plt.plot(x2, df_dtps, color='black')
plt.show()
#print(hps)

"""
"""

while current_line <  len(fileAsList):


    line = fileAsList[current_line].split(" ")
    time = line[1]
    data = line[3].split(',')

    if data[0] == "SPELL_PERIODIC_HEAL":
        owner = data[1].split('-')[0]
        if owner == "Player":
            healing = healing + 

    current_line = current_line + 1



"""


