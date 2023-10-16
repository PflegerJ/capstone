import pymysql
import pandas as pd
import numpy as np
import csv

import warnings



def stringify(v): 
    return "('%s', '%s', %s, %s, %s)" % (v[0], v[1], v[2], v[3], v[4])


def get_from_AWS(boss_ID, difficulty):
    warnings.simplefilter(action='ignore', category=UserWarning)
    connection = {
            'host': '',
            'username': '',
            'password': '',
            'db': ''
    }

    db = pymysql.connect(host=connection['host'], user=connection['username'], password=connection['password'], database=connection['db'])
    cursor = db.cursor()

    # get the fight dataframe 
    if difficulty > 0:
        query = "select * from fight where boss_info_encounter_id =" + boss_ID + " and difficulty = " + str(difficulty)
    else:
        query = "select * from fight where boss_info_encounter_id =" + boss_ID
    dataframe_full = pd.read_sql(query, db)

    # get duration into numpy to replace 0 durations with correct time
    duration_df = dataframe_full['duration']
    duration_np = duration_df.to_numpy()
    duration_list = duration_df.to_list()

    tag_df = dataframe_full['tag']

    # get report code and fight id into numpy arrays to iterate through to get DPS HPS and DTPS
    report_code_df = dataframe_full['report_code']
    report_code_np = report_code_df.to_numpy()

    fight_id_df = dataframe_full['fight_id']
    fight_id_np = fight_id_df.to_numpy()

    #print(report_code_np[647])


    all_fight_data = np.empty(duration_np.shape[0] * 723)
    all_fight_data = all_fight_data.reshape(duration_np.shape[0], 723)

    i = 0

    for index in range(report_code_np.shape[0]):

        fight_data = []
        sql = "SELECT * from dps where (fight_report_code = %(report_code)s) and (fight_fight_id = %(fight_id)s)"
        dps = pd.read_sql(sql, db, params={"report_code":report_code_np[index], "fight_id":fight_id_np[index]})

        sql = "SELECT * from hps where (fight_report_code = %(report_code)s) and (fight_fight_id = %(fight_id)s)"
        hps = pd.read_sql(sql, db, params={"report_code":report_code_np[index], "fight_id":fight_id_np[index]})

        sql = "SELECT * from dtps where (fight_report_code = %(report_code)s) and (fight_fight_id = %(fight_id)s)"
        dtps = pd.read_sql(sql, db, params={"report_code":report_code_np[index], "fight_id":fight_id_np[index]})


            


        time = dps['time'].to_numpy()[-1] / 1000
        duration_np[index] = time

        dps = dps['damage'].to_numpy()

        
        hps = hps['healing'].to_numpy()
        dtps = dtps['damage_taken'].to_numpy()


        if (dps.shape[0] == 242):
            dps = dps[:-1]
            hps = hps[:-1]
            dtps = dtps[:-1]
        elif dps.shape[0] != 241:
            dps = np.zeros(241)
            hps = np.zeros(241)
            dtps = np.zeros(241)
            dps[:] = np.nan
            hps[:] = np.nan
            dtps[:] = np.nan

        fight_data = np.append(dps, hps)
        fight_data = np.append(fight_data, dtps)
        fight_data = np.reshape(fight_data, (1, 723))
        all_fight_data[index] = fight_data
    
        i = i + 1


    tensorflow_data = pd.concat((tag_df, duration_df, pd.DataFrame(all_fight_data)), axis=1)


    tensorflow_data.to_csv(boss_ID + "_" + str(difficulty) + ".csv")
    #print(tensorflow_data)

    """

    #print(dataframe)

    cursor.execute("select * from fight where boss_info_encounter_id = 101118")
    data = cursor.fetchall()
    print(data[0][0])

    #sql = ( "SELECT * from dps where (fight_report_code = %s) and (fight_fight_id = %s)", (data[0][0], data[0][1]) )
    sql = "SELECT * from dps where (fight_report_code = %(report_code)s) and (fight_fight_id = %(fight_id)s)"
    dataframe = pd.read_sql(sql, db, params={"report_code":data[0][0], "fight_id":data[0][1]})
    #cursor.execute(*sql)
    #data = cursor.fetchall()

    #print(dataframe)

    dataframe = dataframe["damage"]



    #dataframe_full['duration'] = duration_df_np
    print(dataframe_full)




    #for row in data:
    #   cursor.execute("")




    # "INSERT IGNORE INTO fight (report_code, fight_id, boss_info_encounter_id, duration, guild_name, server, server_region, tag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (report_code, fight_id, encounter_id, totalTime, guild_name, guild_server, guild_region, kill) )
    """


def getSingleFight(boss_ID, report_code, fight_id, difficulty):
    warnings.simplefilter(action='ignore', category=UserWarning)
    connection = {
            'host': 'enemyinfo.csecqhkmwzyw.us-west-2.rds.amazonaws.com',
            'username': 'admin',
            'password': 'Dokidoki!1',
            'db': 'capstone'
    }

    db = pymysql.connect(host=connection['host'], user=connection['username'], password=connection['password'], database=connection['db'])
    cursor = db.cursor()
    if difficulty > 0:
        query = "select * from fight where boss_info_encounter_id =" + boss_ID + " and difficulty = " + str(difficulty)
    else:
        query = "select * from fight where boss_info_encounter_id =" + boss_ID
    dataframe_full = pd.read_sql(query, db)

    # get duration into numpy to replace 0 durations with correct time
    duration_df = dataframe_full['duration']
    duration_np = duration_df.to_numpy()
    duration_list = duration_df.to_list()

    tag_df = dataframe_full['tag']

    
    fight_data = []
    sql = "SELECT * from dps where (fight_report_code = %(report_code)s) and (fight_fight_id = %(fight_id)s)"
    dps = pd.read_sql(sql, db, params={"report_code":report_code, "fight_id":fight_id})

    sql = "SELECT * from hps where (fight_report_code = %(report_code)s) and (fight_fight_id = %(fight_id)s)"
    hps = pd.read_sql(sql, db, params={"report_code":report_code, "fight_id":fight_id})

    sql = "SELECT * from dtps where (fight_report_code = %(report_code)s) and (fight_fight_id = %(fight_id)s)"
    dtps = pd.read_sql(sql, db, params={"report_code":report_code, "fight_id":fight_id})

    time = dps['time'].to_numpy()[-1] / 1000
    dps = dps['damage'].to_numpy()

    
    hps = hps['healing'].to_numpy()
    dtps = dtps['damage_taken'].to_numpy()


    if (dps.shape[0] == 242):
        dps = dps[:-1]
        hps = hps[:-1]
        dtps = dtps[:-1]
    elif dps.shape[0] != 241:
        dps = np.zeros(241)
        hps = np.zeros(241)
        dtps = np.zeros(241)
        dps[:] = np.nan
        hps[:] = np.nan
        dtps[:] = np.nan

    fight_data = np.append(dps, hps)
    fight_data = np.append(fight_data, dtps)
    fight_data = np.reshape(fight_data, (1, 723))
    #tag_df = pd.DataFrame([1])
    tensorflow_data = pd.concat((pd.DataFrame([1]), pd.DataFrame([time]), pd.DataFrame(fight_data)), axis=1)
    #tensorflow_data = pd.concat((1, time, pd.DataFrame(fight_data)), axis=1)
    tensorflow_data.to_csv(boss_ID + "_" + str(difficulty) +  "SINGLE.csv")
    