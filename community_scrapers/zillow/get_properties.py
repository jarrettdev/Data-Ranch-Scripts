######################################
# Data Ranch Zillow API Kickstart
######################################

#Import packages
################
import requests
import pandas as pd
################

#Optional headers
headers = {'User-Agent' : 'Zillow Tycoon 1.0'}
#Make HTTP GET request to base page
res = requests.get('https://dataranch.info/apizillow_properties/?page=1', headers=headers)
#Retrieve JSON from base page
json_data = res.json()
#Init data list (will be a list of dicts)
data_list = []
#Pagination loop
while True:
    json_data = res.json()
    #Find next page
    next_page = json_data['next']
    print(next_page)
    #for result-dict in list of results
    for result in json_data['results']:
        #Add dict entry
        data_list.append(result)
    #Make dataframe from current list of dicts
    df = pd.DataFrame(data_list)
    #Get duplicates out
    df = df.drop_duplicates()
    #Output to current directory
    df.to_csv('zillow_properties.csv', index=False)
    #Get next page of results
    #Done if no next page
    if not next_page:
        break
    res = requests.get(next_page)

