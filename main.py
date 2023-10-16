import Download_from_warcraft_logs_upload_to_AWS
import getDataforTensorFlowFromAWS
import convertDataToFirstXSeconds
import rnn30
import testSingleLog
# should be the entire pipeline

# flags for what I want program to do
gather_data_API = False
download_data_AWS = True
format_data_30seconds = True
train_model = True

#which_raid = "naxx"
which_raid = "ulduar"
naxx_boss_IDs = {}
ulduar_bosses = [["744", 4, 90], ["745", -1, 30], ["746", -1, 30], ["747", 4, 60], ["748", 4, 200], ["749", -1, 30], ["750", -1, 30], ["751", 4, 45], ["752", 4, 90], ["753", 4, 180], ["754", 4, 270], ["755", 4, 90], ["756", 4, 120], ["757", -1, 30]]

#["744", 4, 90],
difficulty = 4
cut_off_time = 60
step_size = 1
boss_ID = "744"
print("1")
model_acc = []

singleLogTest = False
single_bossID = "749"
report_code = "12DYCcPJtNZaL8qA"
cut_off_time_single = 60
single_difficulty = -1
fightID = 22



def KillPrediction(boss_ID, difficulty, cut_off_time):
    v = 0
    #if singleLogTest:
        #getDataforTensorFlowFromAWS.getSingleFight(single_bossID, "bCh7p41NnfaWc93F", 39, single_difficulty)
        #convertDataToFirstXSeconds.convertSingle(single_bossID + "_" + str(single_difficulty) + "SINGLE.csv", single_bossID + "_" + str(single_difficulty) + "Single_" + str(cut_off_time_single) +".csv", cut_off_time_single)
        #testSingleLog.testSingleLog(single_bossID + "_" + str(single_difficulty) + "Single_" + str(cut_off_time_single) +".csv", 'models\\749_-1_60.model', cut_off_time_single)


    # API calls to warcraft logs and upload data
    if gather_data_API:
        #Download_from_warcraft_logs_upload_to_AWS.getOneLog("bCh7p41NnfaWc93F")
        Download_from_warcraft_logs_upload_to_AWS.getLogs(which_raid)
    # download from AWS
        

    if download_data_AWS:
        getDataforTensorFlowFromAWS.get_from_AWS(boss_ID, difficulty)

        print("Done getting data from AWS")
    # format to first 30 seconds
    if format_data_30seconds:
        convertDataToFirstXSeconds.convert_data(boss_ID, difficulty, cut_off_time)

        print("Done converting data to X seconds")



    # train model
    if train_model:
        v = rnn30.train_model(boss_ID, difficulty, cut_off_time)
        

    return v

for boss in ulduar_bosses:
    model_acc.append(KillPrediction(boss[0], boss[1], boss[2]))

print("Model ACC:")
print(model_acc)
