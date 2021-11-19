# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 11:13:26 2021

This code was written as a test master copy for future redcap-bsi integration. Please fork from here for specific projects 


@author: adwalker
"""
#### =======================================================
## Functions
#### =======================================================

#put this at the end when actually finalizing the program but this needs to stay up here to create variables in the variable explorer

def formatting_time(time_frame):
    """formats the given timeframe for rc and bsi"""
    # dd/mm/YY H:M:S
    rc_return = time_frame.strftime("%Y/%m/%d %H:%M:%S")
    
    # %3Emm%2Fdd%2Fyyyy
    BSI_start_month = time_frame.strftime("%m")
    BSI_start_day = time_frame.strftime("%d")
    BSI_start_year = time_frame.strftime("%y")

    BSI_return = '%3E'+ BSI_start_month + '%2F' + BSI_start_day + '%2F' + BSI_start_year
    
    return rc_return,BSI_return

def prep_file_import(lab_id, repeat_instance, bsi_id, vial_status, vial_location):
    

    text = [
        {
      'lab_id': lab_id, 
      'redcap_repeat_instrument': 'vial_statuses', 
      'redcap_repeat_instance': repeat_instance, 
      'bsi_id': bsi_id, 
      'vial_status': vial_status, 
      'vial_location': vial_location, 
      'test_esm_entry_complete': '2'
      }
        ]
    
    return(text)


def fixing_columns(df,columns):
    # Converting columns to integers and then strings to allow for upload to REDCap
    # Returns df with columns now strings
    
    for i in range(0,len(columns)):
        #df[columns[i]] = df[columns[i]].astype(int)
        #df[columns[i]] = df[columns[i]].astype(str)
        
        df = df.astype({columns[i]:int})
        df = df.astype({columns[i]:str})
                        
    
    return df



def bsi_data_to_redcap(df,redcap_fields,bsi_fields):
    # Function to copy bsi fields into their corresponding redcap fields
    
    if len(redcap_fields) == len(bsi_fields):
        for i in range(0,len(redcap_fields)):
            df[redcap_fields[i]] = df[bsi_fields[i]]
            
    else:   
        print(f"REDCap fields and BSI Fields don't match up for {df}")
        
    return df


#Almost figured this out just need to fix the index of merge field to match with length

def add_unique_identifier(df,fields_to_merge,new_field_name):
    
    merged_value = ''
    for i, merge_field in enumerate(fields_to_merge):
        if i + 1 == len(fields_to_merge): ## if last value
                merged_value = merged_value + df[merge_field].astype(str)
        else: ## every other value
            merged_value = merged_value + df[merge_field].astype(str)+"_"

    df[new_field_name] = merged_value
    return df
    
    #test['id_date2']=test['lab_id'].astype(str)+"_"+test['levitt_draw_date'].astype(str) ## This is the one that works




#if __name__ == '__main__':
#    main()






#### ===========================================================
## Setting up imports
#### ===========================================================

import requests
import json
import pandas as pd
import numpy as np
from io import StringIO
import datetime
from redcap import Project, RedcapError
import io


# ---------------------------------------------------------------

#def main():  ## Use this when you're finalizing the program

#### =============================================================
## Importing Data from config file
#### =============================================================

import rc_bsi_config as config 
overall_study_id_variable = config.overall_study_id_variable

#### =============================================================
## Setting up global variables
#### =============================================================


now = datetime.datetime.now()

#test timeframes
one_week_ago = now - datetime.timedelta(days=7)
two_weeks_ago = now - datetime.timedelta(days=14)
two_months_ago = now - datetime.timedelta(days=60)

#timeframe as chosen in config file
desired_time_ago = now - datetime.timedelta(days=config.BSI_DATA_fields["BSI_days_ago_update_cadence"])

query_start_time = formatting_time(desired_time_ago)

#### =============================================================
## Getting data from REDCap
#### =============================================================
rc_date_range_begin = query_start_time[0]
rc_date_range_end = formatting_time(now)[0]

URL = config.RC_API_login["URL"]
API_KEY = config.RC_API_login["API_KEY"]
project = Project(URL, API_KEY)


fields_of_interest = config.RC_DATA_fields["fields_of_interest"]
forms_of_interest = config.RC_DATA_fields["forms_of_interest"]
rc_import_df = project.export_records(fields=fields_of_interest,forms=forms_of_interest,format='df',df_kwargs={'index_col': project.field_names[0]}).reset_index()
rc_import_df = rc_import_df.replace({np.nan: ''})

#### ==========================================================
## Getting data from BSI
#### ==========================================================


##getting initial bsi_session_id
headers = {
    'Content-Type':'application/x-www-form-urlencoded',
    'Accept':'text/plain'}

data = config.BSI_API_login

login_url = config.BSI_DATA_fields["BSI_url"] + "/common/logon"


response = requests.request("POST",login_url,headers=headers,data=data)
bsi_session_id = response.text

## Doublechecking that the session is valid
headers = {
    'Content-Type':'application/json',
    'BSI-SESSION-ID': bsi_session_id}

ping_url = config.BSI_DATA_fields["BSI_url"] + "/common/ping"
response = requests.request("POST",url = ping_url, headers=headers)


##Querrying wanted BSI report


headers = {
    'Content-Type':'application/json',
    'BSI-SESSION-ID': bsi_session_id}


#This url is specific to this project and these fields pulled; need to get a new URL from swagger or write script to create url based off user selected fields
#url = config.BSI_DATA_fields["BSI_url"] + config.BSI_DATA_fields["BSI_report_extension_1"]+query_start_time[1]+config.BSI_DATA_fields["BSI_report_exension_2"]

url = config.BSI_DATA_fields["BSI_url_without_time_criteria"] + config.BSI_DATA_fields["BSI_url_time_constraint"]+query_start_time[1]  #Could shorten this in the config file if wanted

bsi_r = requests.request("GET",url,headers=headers)
bsi_data = json.loads(bsi_r.text)
columns = bsi_data['headers']
bsi_import_df = pd.DataFrame(bsi_data['rows'], columns=columns)

# Adding new column for truncated date
bsi_import_df['short_date'] = bsi_import_df['Date Vial Modified'].str[:10]



#### ======================================================
## Crosstalking the two datasets
#### ======================================================

""" 
Idea for how to crosstalk for levitt study:

"""

## Adding column for id+date within both df's

add_unique_identifier(df,fields_to_merge,new_field_name)





## Creates new df that only has vials that were in REDCap and have been modified in the past two weeks in BSI
existing_vials =  pd.merge(rc_import_df,bsi_import_df,how='inner',left_on='bsi_id',right_on='BSI ID')
bool_to_erase_unchanged_vials = existing_vials['vial_status']==existing_vials['Vial Status']
existing_vials_needing_change = existing_vials[~bool_to_erase_unchanged_vials]



## Removing existing vials to keep only new vials
bool_to_erase_old_vials = bsi_import_df["BSI ID"].isin(existing_vials["bsi_id"])
new_vials = bsi_import_df[~bool_to_erase_old_vials]


#M# Matching all Redcap entries with their matching bsi data
new_vials_merged = pd.merge(rc_import_df,new_vials,how='inner',left_on='draw_sample_id',right_on='Sample ID')




#### ======================================================
## Updating old REDCap Vials
#### ======================================================


## Updating Vial Statuses for those that need changing
existing_vials_needing_change_updated_status = pd.DataFrame.copy(existing_vials_needing_change)
existing_vials_needing_change_updated_status['vial_status'] = existing_vials_needing_change_updated_status['Vial Status']


## Taking only wanted columns
exporting_existing_vials = existing_vials_needing_change_updated_status[[overall_study_id_variable,'redcap_event_name','redcap_repeat_instrument','redcap_repeat_instance','bsi_id','vial_status','rc_mat_type','rc_vial_comment','vial_statuses_complete']]


## Fixing cell formatting
exporting_existing_vials = fixing_columns(exporting_existing_vials,['redcap_repeat_instance','vial_statuses_complete'])

## Setting proper index
exporting_existing_vials = exporting_existing_vials.set_index([overall_study_id_variable,'redcap_event_name'])


#### ======================================================
## Updating new Vials
#### ======================================================

## Correcting column information
new_vials_merged = new_vials_merged.assign(redcap_repeat_instrument="vial_statuses")
new_vials_merged = new_vials_merged.assign(redcap_repeat_instance="new")
new_vials_merged = new_vials_merged.assign(vial_statuses_complete="2")


## Taking only wanted columns
redcap_fields = ['bsi_id','vial_status','rc_mat_type','rc_vial_comment']
bsi_fields = ['BSI ID','Vial Status','Material Type','Comment']
new_vials_merged = bsi_data_to_redcap(new_vials_merged,redcap_fields,bsi_fields)
new_vials_merged = new_vials_merged.drop(columns=['draw_sample_id','draw_information_complete'])


last_col = "vial_statuses_complete"
last_col_loc = new_vials_merged.columns.get_loc(last_col)+1

new_vials_merged = new_vials_merged.drop(new_vials_merged.iloc[:,last_col_loc:len(new_vials_merged.columns)],axis = 1)


##Setting proper index for export
exporting_new_vials = new_vials_merged.set_index([overall_study_id_variable,'redcap_event_name'])


#### ======================================================
## submitting files to REDCap
#### ======================================================

dry_run = True

if dry_run :
    print("dry")
else :
    old_vials_response = project.import_records(exporting_existing_vials,format='df')
    new_vials_response = project.import_records(exporting_new_vials,format='df')




#### ======================================================
## Logging out of BSI
#### ======================================================
headers = {
    'Content-Type':'application/json',
    'BSI-SESSION-ID': bsi_session_id}

url = config.BSI_DATA_fields["BSI_url"] + "/common/logoff"
response = requests.request("POST",url = url, headers=headers)





