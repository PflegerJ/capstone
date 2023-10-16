import interpolation
import pandas as pd
import csv
import matplotlib.pyplot as plt
import numpy as np



def convert_data(boss_ID, difficulty, cut_off_time):

    file_in = boss_ID + "_" + str(difficulty) + '.csv'
    file_out = boss_ID + "_" + str(difficulty) + '_' + str(cut_off_time) + '.csv'
    df = pd.read_csv(file_in)


    tag_df = df['tag']
    duration = df['duration']
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    df.drop(columns=df.columns[0], axis=1, inplace=True)


    all_fight_data = np.empty(duration.shape[0] * ((cut_off_time * 3) + 1))
    all_fight_data = all_fight_data.reshape(duration.shape[0], ((cut_off_time * 3) + 1))

    for i in range(df.shape[0]):
        dps = df.iloc[i][0:241].values
        hps = df.iloc[i][241:482].values
        dtps = df.iloc[i][482:].values

        dur = duration[i]
        if i == 56:
            z =2

        dps_i, hps_i, dtps_i = interpolation.interpolate(dps, hps, dtps, duration[i], cut_off_time, 1)
        dps_i = np.array(dps_i)
        hps_i = np.array(hps_i)
        dtps_i = np.array(dtps_i)
        data = np.array(tag_df[i])
        data = np.append(data, dps_i[0:cut_off_time])
        data = np.append(data, hps_i[0:cut_off_time])
        data = np.append(data, dtps_i[0:cut_off_time])

        all_fight_data[i] = data

        #print(data)
        #print('a)')
        
        """
        x1 = np.arange(1, cut_off_time + 1, 1)
        time_step = duration[i] / 241
        #x2 = np.arange(0, duration[i], time_step)
        end = cut_off_time / time_step 
        x2 = np.arange(0, int(end))
        plt.plot(x1, dtps_i, color="blue")

        x2 = np.arange(0, duration[i], time_step)
        plt.plot(x2, dtps, color="red", linestyle='dashed')
        """
        """
        if end < duration[i]:
            x2 = np.arange(0, cut_off_time, time_step)
            plt.plot(x2[:len(dtps[:int(end)])], dtps[:int(end)], color="red")
        else:
            x2 = np.arange(0, duration[i], time_step)
            plt.plot(x2, dtps, color="red")
        
        plt.show()
        """
        

    df = pd.DataFrame(all_fight_data)
    df.to_csv(file_out)

def convertSingle(file_in, file_out, cut_off_time):
    df = pd.read_csv(file_in)
    tag = df.iloc[0][1]
    duration = df.iloc[0][2]
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    df.drop(columns=df.columns[0], axis=1, inplace=True)

    all_fight_data = np.empty(((cut_off_time * 3) + 1))


    dps = df.iloc[0][0:241].values
    hps = df.iloc[0][241:482].values
    dtps = df.iloc[0][482:].values


    dps_i, hps_i, dtps_i = interpolation.interpolate(dps, hps, dtps, duration, cut_off_time, 1)
    dps_i = np.array(dps_i)
    hps_i = np.array(hps_i)
    dtps_i = np.array(dtps_i)
    data = np.array(tag)
    data = np.append(data, dps_i[0:cut_off_time])
    data = np.append(data, hps_i[0:cut_off_time])
    data = np.append(data, dtps_i[0:cut_off_time])
    data = data.reshape(1, (cut_off_time * 3) + 1)
    z =2
    df = pd.DataFrame(data)
    df.to_csv(file_out)




