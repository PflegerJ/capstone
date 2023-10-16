import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import Get_Data_From_Combat_Log
import tensorflow as tf
from keras.models import load_model
import numpy as np
import time
import matplotlib.pyplot as plt
import pandas as pd

"""

"Kologarn"  749     60      -1
"Mimiron"   754     270     4 
"Freya"     753     180     4
"The Iron Council"  748     200    4
"Algalon" 757 30 -1
"""




filename = "C:\\Program Files (x86)\\World of Warcraft\\_classic_\\Logs\\WoWCombatLog-031523_200700.txt"

boss_name = "Freya"
bossID =  753
cut_off_time = 180
difficulty = 4

# start wait timer
print("Waiting for cut off time: " + str(cut_off_time))
time.sleep(cut_off_time + 20)
print("Grabbing combat log information...")
# grab combatlog and get data
dps, hps, dtps = Get_Data_From_Combat_Log.getInfoFromLog(filename, cut_off_time, boss_name)

x_values = np.arange(0, cut_off_time)

# smooth the data
dps_poly = np.polyfit(x_values, dps, deg=10)
hps_poly = np.polyfit(x_values, hps, deg=10)
dtps_poly = np.polyfit(x_values, dtps, deg=10)

dps_smoothed = np.polyval(dps_poly, x_values)
hps_smoothed = np.polyval(hps_poly, x_values)
dtps_smoothed = np.polyval(dtps_poly, x_values)


for x in x_values:
    if dps_smoothed[x] < 0:
        dps_smoothed[x] = 0
    if hps_smoothed[x] < 0:
        hps_smoothed[x] = 0
    if dtps_smoothed[x] < 0:
        dtps_smoothed[x] = 0

if len(dps) < cut_off_time:
    zeros = np.zeros(cut_off_time - len(dps))
    dps.append(zeros)
    hps.append(zeros)
    dtps.append(zeros)

all_data = []
all_data.append(dps_smoothed)
all_data.append(hps_smoothed)
all_data.append(dtps_smoothed)
all_data = np.array(all_data).T

tf_data = np.array(all_data)
tf_data = tf_data.reshape(1, cut_off_time, 3)


#print(tf_data)

#print(tf_data.shape)

z =2
# run it against the model

x1 = np.arange(0, len(hps), 1)
x3 = np.arange(0, len(dps), 1)
x4 = np.arange(0, len(dtps), 1)
plt.plot(x_values, hps_smoothed, color="blue")
plt.plot(x_values, dps_smoothed, color="green")
plt.plot(x_values, dtps_smoothed, color="yellow")
#plt.show()


df_dps = pd.read_csv("koloDPS.csv")
df_hps = pd.read_csv("koloHPS.csv")
df_dtps = pd.read_csv("koloDTPS.csv")



print("Making Prediction...")
model_path = "models\\" + str(bossID) + "_" + str(difficulty) + "_" + str(cut_off_time) + ".model'"
#print(model_path)
loaded_model = load_model('models\\' + str(bossID) + '_' + str(difficulty) + "_" + str(cut_off_time) + '.model')
result = loaded_model.predict(tf_data)




if result[0][0] > 0.5:
    print("Result: Wipe " + str(result[0][0]) + "%")
else:
    print("Result: Kill " + str(result[0][1]) + "%")
print(result)

# print prediction