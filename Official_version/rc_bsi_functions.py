# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 15:58:51 2021

@author: adwalker
"""

import datetime

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