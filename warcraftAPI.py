import json
import requests
import sys

# funciton to get OAuth 2.0 token for Warcraft logs API 2.0 calls
def get_new_token():
    auth_server_url = 'https://www.warcraftlogs.com/oauth/token' 
    client_id = '976a4a41-33ff-4e8e-a760-e1c39ec8daa6'
    client_secret = ''

    token_req_payload = {'grant_type': 'client_credentials'}

    token_response = requests.post( auth_server_url,
    data = token_req_payload, verify = False, allow_redirects = False,
    auth = ( client_id, client_secret ) )
    if ( token_response.status_code !=200 ):
        print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
        sys.exit(1)
        
    print("Successfuly obtained a new token")
    tokens = json.loads(token_response.text)
    return tokens['access_token']


# function that does the API call for data
# pass in the graphQL query and arguments with the auth token
def apiCall(query, vars, auth_token):
    api_url = 'https://classic.warcraftlogs.com/api/v2/client'
    api_call_headers = {'Authorization': 'Bearer ' + auth_token}


    api_call_response = requests.post(api_url, json = {"query": query, 'variables': vars}, headers=api_call_headers, verify = True)
    return api_call_response.json()



def getSourceID(reportCode, auth_token, name):

    source_id_vars = {'reportCode': reportCode}
    source_id_query = """query report($reportCode: String!) {
    reportData {
        report (code: $reportCode) {
            playerDetails (endTime: 1000000000000)
        }
    }
    }"""



    logz = apiCall(source_id_query, source_id_vars, auth_token)
    if logz['data']['reportData']['report'] != None: 
        characters = logz['data']['reportData']['report']['playerDetails']['data']['playerDetails']['dps']
        for toon in characters:
            if (toon['name'] == name):
                return toon['id']
    
    return "NA"

def getPageOfLogs(pageNumber, auth_token, boss_ID):
    full_boss_list_vars = {'bossID': boss_ID,
    'pageNumber': pageNumber}
    full_boss_list_query = """query full_boss_list($bossID: Int!, $pageNumber: Int!) {
        worldData {
            encounter(id: $bossID) {
                characterRankings (className: "Priest", specName: "Shadow", page: $pageNumber, serverRegion: "us")
            }
        }
    }"""

    return apiCall(full_boss_list_query, full_boss_list_vars, auth_token)

def getFights(report_code, auth_token):

    fight_list_var = {'reportCode': report_code}
    fight_list_query = """query fight_list($reportCode: String!) {
	    reportData {
		    report (code: $reportCode) {
			    fights {
				    id
				    difficulty
                    kill	
                    encounterID
                    startTime
                    endTime
                    hardModeLevel
			    }
            }
        }
    }"""

    return apiCall(fight_list_query, fight_list_var, auth_token)

def get_fight_summary(report_code, fightID, auth_token):
    fight_summary_var = {'reportCode': report_code, 'ID': fightID}
    fight_summary_query = """query fightSummary($reportCode: String!, $ID: [Int]) {
	    reportData {
		    report (code: $reportCode) {
			    table (fightIDs: $ID, endTime: 10000000) 		
		    }
	    }
    }"""

    return apiCall(fight_summary_query, fight_summary_var, auth_token)

def get_enemy_info(report_code, fightID, auth_token):
    enemy_info_var = {'reportCode': report_code, 'ID': fightID}
    enemy_info_query = """query fightSummary($reportCode: String!, $ID: [Int]) {
	    reportData {
		    report (code: $reportCode) {
			    table (hostilityType: Enemies, fightIDs: $ID, endTime: 10000000) 		
		    }
	    }
    }"""

    return apiCall(enemy_info_query, enemy_info_var, auth_token)

def get_damage_info(report_code, fightID, sourceID, auth_token):
    damage_done_var = {'reportCode': report_code, 'ID': fightID, 'sourceID': sourceID}
    damage_done_query = """query damage_done ($reportCode: String!, $ID: [Int], $sourceID: Int!) {
	    reportData {
            report (code: $reportCode) {
                table (dataType: DamageDone, fightIDs: $ID, endTime: 10000000000000, sourceID: $sourceID) 
            }
        }
    }"""
    return apiCall(damage_done_query, damage_done_var, auth_token)

def get_graph(report_code, fightID, startTime, endTime, auth_token):
    graph_var = {'reportCode': report_code, 'ID': fightID, 'startTime': startTime, 'endTime': endTime}
    graph_query = """query graph ($reportCode: String!, $ID: [Int], $startTime: Float!, $endTime: Float!) {
	    reportData {
		    report (code: $reportCode) {
			    graph(startTime: $startTime, endTime: $endTime, fightIDs: $ID)
		    }
	    }
    }"""

    return apiCall(graph_query, graph_var, auth_token)

def get_guild_info(report_code, auth_token):
    guild_info_var = {'reportCode': report_code}
    guild_info_query = """query guild_info ($reportCode: String!) {
	    reportData {
            report (code: $reportCode) {
                guild {
					name
					server {
						name, 
						region {
                            name
                        }
					}
				}
            }   
        }
    }"""

    return apiCall(guild_info_query, guild_info_var, auth_token)

def getSpeedLogs(pageNumber, auth_token, boss_ID):
    full_boss_list_vars = {'bossID': boss_ID, 'pageNumber': pageNumber}
    full_boss_list_query = """query full_boss_list($bossID: Int!, $pageNumber: Int!) {
        worldData {
            encounter(id: $bossID) {
                fightRankings (metric: speed, page: $pageNumber, serverRegion: "us")
            }
        }
    }"""

    return apiCall(full_boss_list_query, full_boss_list_vars, auth_token)

def getPlayerDmgOnOneBoss(playerName, auth_token, boss_ID):
    vars = {'bossID': boss_ID, 'playerName': playerName}
    query = """query characterRank($playerName: String!, $bossID: Int!)
                {
	                characterData  
	                {
		                character (name: $playerName, serverSlug: "whitemane", serverRegion: "US")		
                        {
			                encounterRankings (compare: Rankings, metric: dps, encounterID: $bossID) 		
		                }
	                }   
                }
            """
    return apiCall(query, vars, auth_token)

def getFightIDs(report_code, auth_token):
    fight_list_var = {'reportCode': report_code}
    fight_list_query = """query fight_list($reportCode: String!) {
	    reportData {
		    report (code: $reportCode) {
			    fights (encounterID: 755) {
				    id
			    }
            }
        }
    }"""
    return apiCall(fight_list_query, fight_list_var, auth_token)

def getPlayerInfo(report_code, auth_token, fightID):
    vars = {'reportCode': report_code, 'fightID': fightID}
    query = """query fight_list ($reportCode: String!, $fightID: [Int])
                {
	                reportData 
	                {
		                report (code: $reportCode) 
		                {
			                playerDetails (fightIDs: $fightID)
		                }
	                }
                }"""
    return apiCall(query, vars, auth_token)


def getShadowCrash(report_code, auth_token, fightID):
    vars = {'reportCode': report_code, 'fightID': fightID}
    query = """query fight_list2 ($reportCode: String!, $fightID: [Int])
                {
	                reportData 
	                {
		                report (code: $reportCode) 
		                {
			                events (encounterID: 755, abilityID: 62659, fightIDs: $fightID, dataType: DamageTaken)
			                {
				                data
			                }
		                }
	                }
                }"""
    return apiCall(query, vars, auth_token)