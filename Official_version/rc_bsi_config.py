# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 10:16:30 2021

@author: adwalker
"""

your_studys_redcap_API_key = '43A4F5F6F04453683EE5558E2FF7D482'
overall_study_id_variable = 'lab_id'
RC_form_with_identifying_information ='levitt_draw_data' # might need to be more specific than just the entire form if there are issues of phi


BSI_internal_study_id = "LTS"
BSI_DISPLAY_fields = list({
    
    "vial.study_id", #ID for the study
    "vial.bsi_id", 
    "vial.mat_type", #Material type for sample
    "vial.vial_status",
    "vial.date_modified", #REQUIRED, Last time this sample was modified in BSI
    "vial.sample_id",
    "vial.field_229", #vial data for comment
    "vial.seq_num"
    
    })



# %% Don't modify code below this line



RC_API_login = {
    "URL": 'https://redcap.med.usc.edu/api/',
    "API_KEY": your_studys_redcap_API_key
    }

RC_DATA_fields = {
    "overall_study_id_variable": overall_study_id_variable,
    "fields_of_interest":[overall_study_id_variable],
    "forms_of_interest":[RC_form_with_identifying_information,'vial_statuses']  #In this case, levitt_draw_data is a field of interest because it contains identifier information for these patients to allow for cross referencing to bsi
    }

BSI_API_login = {
        'user_name': 'WSI_AI_API_Access',
        'password': 'L%ZSQU&6F4hVqHe%zyNJqmRGz%QdtuPtqp##FBz'  ## Password will need to be updated yearly 
    }


bsi_sample_url = ''
for display_field in BSI_DISPLAY_fields:
    bsi_sample_url = bsi_sample_url + "display_fields=" + display_field + "&"


BSI_DATA_fields = {
    "BSI_url": "https://bsishra-btp-web-mirror-websvc.bsisystems.com/api/rest/CHLA_PRB",
    
    "BSI_url_without_time_criteria":'https://bsishra-btp-web-mirror-websvc.bsisystems.com/api/rest/CHLA_PRB/reports/list?' + bsi_sample_url + 'criteria=vial.study_id%3D' + BSI_internal_study_id + '&sort_fields=vial.date_entered&limit=10000&type=1',
    "BSI_url_time_constraint": '&criteria=vial.date_modified',
    "BSI_days_ago_update_cadence": 60
    }






#url = 'https://bsishra-btp-web-mirror-websvc.bsisystems.com/api/rest/CHLA_PRB/reports/list?display_fields=vial.study_id&display_fields=vial.bsi_id&display_fields=vial.mat_type&display_fields=%2Bvial.vial_status&display_fields=vial.date_modified&display_fields=vial.sample_id&display_fields=vial.field_229&display_fields=vial.seq_num&criteria=vial.study_id%3DLTS&sort_fields=vial.date_entered&limit=10000&type=1&criteria=vial.date_modified' + query_start_time[1]
