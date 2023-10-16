import warcraftAPI
import pymysql



def stringify(v): 
    return "('%s', '%s', %s, %s, %s)" % (v[0], v[1], v[2], v[3], v[4])

def getLogs(which_raid):
    connection = {
            'host': '',
            'username': '',
            'password': '',
            'db': ''
    }

    db = pymysql.connect(host=connection['host'], user=connection['username'], password=connection['password'], database=connection['db'])

    curser = db.cursor()

    curser.execute("select * from boss_info")
    data = curser.fetchall()
    print(data)
    # get OAuth 2.0 token
    auth_token = warcraftAPI.get_new_token()

    # get the first page of patchwork logs
    boss_ID = ""

    if which_raid == 'naxx':
        boss_ID = 101118

    elif which_raid == 'ulduar':
        boss_ID = 744

    for i in range(1, 21):
        page_of_logs = warcraftAPI.getPageOfLogs(i, auth_token, boss_ID)
        page_of_logs = page_of_logs['data']['worldData']['encounter']['characterRankings']

        #page_of_logs = warcraftAPI.getSpeedLogs(i, auth_token, boss_ID)
        #page_of_logs = page_of_logs['data']['worldData']['encounter']['fightRankings']
        for log in page_of_logs['rankings']:
            valid_data = True
            report_code = log['report']['code']

            guild_info = warcraftAPI.get_guild_info(report_code, auth_token)
            guild_info = guild_info['data']['reportData']['report']['guild']

            if guild_info == None:
                guild_name = ""
                guild_server = ""
                guild_region = ""
            else:
                guild_name = guild_info['name']
                guild_server = guild_info['server']['name']
                guild_region = guild_info['server']['region']['name']

            # get list of all fights in the report
            fight_list = warcraftAPI.getFights(report_code, auth_token)
            fight_list = fight_list['data']['reportData']['report']['fights']

            # go through each fight
            for fight in fight_list:

                # fight is a boss fight
                if fight['difficulty'] == 3:

                    # get the fight ID, enounterId and if it was a kill or not (True is kill)
                    fight_id = fight['id']
                    encounter_id = fight['encounterID']
                    kill = fight['kill']
                    hardMode = fight['hardModeLevel']

                    if kill:
                        kill = 1
                    else:
                        kill = 0
                    
                    if kill == 1:
                        startTime = fight['startTime']
                        endTime = fight['endTime']

                        summary = warcraftAPI.get_fight_summary(report_code, fight_id, auth_token)
                        summary = summary['data']['reportData']['report']['table']['data']

                        totalTime = summary['totalTime'] / 1000
                        itemLevel = summary['itemLevel']


                        graph = warcraftAPI.get_graph(report_code, fight_id, startTime, endTime, auth_token)
                        graph = graph['data']['reportData']['report']['graph']['data']['series']

                        interval = graph[0]['pointInterval']
                        damage_done = graph[0]['data']
                        damage_taken = graph[1]['data']
                        healing_done = graph[2]['data']

                        if len(damage_done) < 250:

                            print(len(damage_done), " ", len(damage_taken), " ", len(healing_done))
                            
                            print("kill: ", kill)
                            print(type(fight_id))
                            
                            damage_done_tuple = []
                            healing_done_tuple = []
                            damage_taken_tuple = []
                            time = 0
                            for i in range (len(damage_done)):
                                damage_done_tuple.append((report_code, fight_id, encounter_id, damage_done[i], time))
                                healing_done_tuple.append((report_code, fight_id, encounter_id, healing_done[i], time))
                                damage_taken_tuple.append((report_code, fight_id, encounter_id, damage_taken[i], time))
                                time += interval

                            damage_string = map(stringify, damage_done_tuple)
                            healing_string = map(stringify, healing_done_tuple)
                            damage_taken_string = map(stringify, damage_taken_tuple)

                            damage_batchData = ", ".join(e for e in damage_string)
                            healing_batchData = ", ".join(e for e in healing_string)
                            damage_taken_batchData = ", ".join(e for e in damage_taken_string)


                            sql = ("INSERT IGNORE INTO fight (report_code, fight_id, boss_info_encounter_id, duration, guild_name, server, server_region, difficulty, tag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (report_code, fight_id, encounter_id, totalTime, guild_name, guild_server, guild_region, hardMode, kill) )
                            curser.execute(*sql)
                            db.commit()


                            sql = ("INSERT IGNORE INTO dps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, damage, time) VALUES %s" % damage_batchData)
                            curser.execute(sql)
                            db.commit()       


                            sql = ("INSERT IGNORE INTO hps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, healing, time) VALUES %s" % healing_batchData)
                            curser.execute(sql)
                            db.commit()

                            sql = ("INSERT IGNORE INTO dtps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, damage_taken, time) VALUES %s" % damage_taken_batchData)
                            curser.execute(sql)
                            db.commit()
                            
                            
                            print("report info: ", report_code, " ", fight_id)

                """
                
                for damage in damage_done:
                    sql = ("INSERT IGNORE INTO dps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, damage, time) VALUES (%s, %s, %s, %s, %s)", (report_code, fight_id, encounter_id, damage, time))
                    curser.execute(*sql)
                    db.commit()
                    time += interval

                time = 0
                for healing in healing_done:
                    sql = ("INSERT IGNORE INTO hps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, healing, time) VALUES (%s, %s, %s, %s, %s)", (report_code, fight_id, encounter_id, healing, time))
                    curser.execute(*sql)
                    db.commit()
                    time += interval
                
                time = 0
                for damage in damage_taken:
                    sql = ("INSERT IGNORE INTO dtps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, damage_taken, time) VALUES (%s, %s, %s, %s, %s)", (report_code, fight_id, encounter_id, damage, time))
                    curser.execute(*sql)
                    db.commit()
                    time += interval

                """



                """
                #get number of healers
                player_details_healers = summary['playerDetails']['healers']
                number_of_healers = 0
                for healer in player_details_healers:
                    number_of_healers += 1
            
                #get Healing per second
                summary_healing = summary['healingDone']
                total_healing = 0
                for healing in summary_healing:
                    if healing['type'] != 'Boss':
                        total_healing += healing['total']

                #get damage taken per second
                summary_damage_taken = summary['damageTaken']
                total_damage_taken = 0
                for damage_taken in summary_damage_taken:
                    total_damage_taken += damage_taken['total']

                #get DPS
                damage_done = summary['damageDone']
                total_damage_done = 0
                for player in damage_done:
                    total_damage_done += player['total']


                #get first death
                death_events = summary['deathEvents']
                first_death_event = None
                if len(death_events) > 0:
                    first_death_event = death_events[0]['deathTime']
                """


def getOneLog(report_code):
    connection = {
            'host': 'enemyinfo.csecqhkmwzyw.us-west-2.rds.amazonaws.com',
            'username': 'admin',
            'password': 'Dokidoki!1',
            'db': 'capstone'
    }

    db = pymysql.connect(host=connection['host'], user=connection['username'], password=connection['password'], database=connection['db'])

    curser = db.cursor()

    curser.execute("select * from boss_info")
    data = curser.fetchall()
    print(data)
    # get OAuth 2.0 token
    auth_token = warcraftAPI.get_new_token()

    guild_info = warcraftAPI.get_guild_info(report_code, auth_token)
    guild_info = guild_info['data']['reportData']['report']['guild']

    if guild_info == None:
        guild_name = ""
        guild_server = ""
        guild_region = ""
    else:
        guild_name = guild_info['name']
        guild_server = guild_info['server']['name']
        guild_region = guild_info['server']['region']['name']

    fight_list = warcraftAPI.getFights(report_code, auth_token)
    fight_list = fight_list['data']['reportData']['report']['fights']

    # go through each fight
    for fight in fight_list:

        # fight is a boss fight
        if fight['difficulty'] == 3:

            # get the fight ID, enounterId and if it was a kill or not (True is kill)
            fight_id = fight['id']
            encounter_id = fight['encounterID']
            kill = fight['kill']
            hardMode = fight['hardModeLevel']

            if kill:
                kill = 1
            else:
                kill = 0
            
            if kill == 1:
                startTime = fight['startTime']
                endTime = fight['endTime']

                summary = warcraftAPI.get_fight_summary(report_code, fight_id, auth_token)
                summary = summary['data']['reportData']['report']['table']['data']

                totalTime = summary['totalTime'] / 1000
                itemLevel = summary['itemLevel']


                graph = warcraftAPI.get_graph(report_code, fight_id, startTime, endTime, auth_token)
                graph = graph['data']['reportData']['report']['graph']['data']['series']

                interval = graph[0]['pointInterval']
                damage_done = graph[0]['data']
                damage_taken = graph[1]['data']
                healing_done = graph[2]['data']

                if len(damage_done) < 250:

                    print(len(damage_done), " ", len(damage_taken), " ", len(healing_done))
                    
                    print("kill: ", kill)
                    print(type(fight_id))
                    
                    damage_done_tuple = []
                    healing_done_tuple = []
                    damage_taken_tuple = []
                    time = 0
                    for i in range (len(damage_done)):
                        damage_done_tuple.append((report_code, fight_id, encounter_id, damage_done[i], time))
                        healing_done_tuple.append((report_code, fight_id, encounter_id, healing_done[i], time))
                        damage_taken_tuple.append((report_code, fight_id, encounter_id, damage_taken[i], time))
                        time += interval

                    damage_string = map(stringify, damage_done_tuple)
                    healing_string = map(stringify, healing_done_tuple)
                    damage_taken_string = map(stringify, damage_taken_tuple)

                    damage_batchData = ", ".join(e for e in damage_string)
                    healing_batchData = ", ".join(e for e in healing_string)
                    damage_taken_batchData = ", ".join(e for e in damage_taken_string)


                    sql = ("INSERT IGNORE INTO fight (report_code, fight_id, boss_info_encounter_id, duration, guild_name, server, server_region, difficulty, tag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (report_code, fight_id, encounter_id, totalTime, guild_name, guild_server, guild_region, hardMode, kill) )
                    curser.execute(*sql)
                    db.commit()


                    sql = ("INSERT IGNORE INTO dps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, damage, time) VALUES %s" % damage_batchData)
                    curser.execute(sql)
                    db.commit()       


                    sql = ("INSERT IGNORE INTO hps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, healing, time) VALUES %s" % healing_batchData)
                    curser.execute(sql)
                    db.commit()

                    sql = ("INSERT IGNORE INTO dtps (fight_report_code, fight_fight_id, fight_boss_info_encounter_id, damage_taken, time) VALUES %s" % damage_taken_batchData)
                    curser.execute(sql)
                    db.commit()
                    
                    
                    print("report info: ", report_code, " ", fight_id)