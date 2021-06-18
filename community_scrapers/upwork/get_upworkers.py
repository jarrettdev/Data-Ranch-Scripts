######################################
# Data Ranch Upwork API Kickstart
######################################

#Import packages
################
import requests
import json
import pandas as pd
################

#Optional headers
headers = {'User-Agent' : 'Upwork Tycoon 1.0'}
#Make HTTP GET request to base page
res = requests.get('https://dataranch.info/apiupwork_freelancers/?page=1', headers=headers)
#Retrieve JSON from base page
json_data = res.json()
#Init upworker list (will be a list of dicts)
upworker_list = []
#Pagination loop
while True:
    json_data = res.json()
    #Find next page
    next_page = json_data['next']
    print(next_page)
    #Done if no next page
    if not next_page:
        break
    #for result-dict in list of results
    for result in json_data['results']:
        #Add dict entry
        upworker_list.append(result)
    #Make dataframe from current list of dicts
    df = pd.DataFrame(upworker_list)
    #Get duplicates out
    df = df.drop_duplicates()
    #Output to current directory
    df.to_csv('upworkers.csv', index=False)
    #Get next page of results
    res = requests.get(next_page)

