####################################################
#                  Revision: 1.0                   #
#              Updated on: 11/12/2015              #
####################################################

####################################################
#                                                  #
#   This file check Read & Write errors, extracts  #
#   data for construnction & reconstrunction time  #
#   for each Disk, F2, & F3 Menu. Which are useful #
#   to generate report.                            #
#                                                  #
#   Author: Zankar Sanghavi                        #
#                                                  #
#   © Dot Hill Systems Corporation                 #
#                                                  #
####################################################
import time

import os
import sys
c_path = os.getcwd()

import raid_fault_functions
import generate_word_raid_fault

rff = raid_fault_functions.Raid_Fault_Functions
gwrf = generate_word_raid_fault.Generate_Word_Raid_Fault


###################################
#  Importing from other Directory
###################################

sys.path.insert(0, r''+str(c_path)+'/Common Scripts')
import user_inputs_ICS
import fixed_data_ICS
import report_functions
import extract_lists
import modify_word_docx

sys.path.insert(0, r''+str(c_path)+'/IO Stress')
import log_functions


###################################
#  Importing from Current Directory
###################################
sys.path.insert(0, r''+str(c_path)+'/Cable Pulls')
import pandas
import csv
import numpy as np
import extract_f2_f3
import generate_word_cable_pulls
import time

from docx import Document
from docx.shared import Inches
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.table import WD_TABLE_DIRECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Cm
import re



###################################
#  To call functions from different
#  files. 
###################################
lf= log_functions.Log_Functions
ed= extract_f2_f3.Extract_F2_F3
ui= user_inputs_ICS.User_Inputs
fd= fixed_data_ICS.Fixed_Data
rf= report_functions.Report_Functions
gwcp= generate_word_cable_pulls.Generate_Word_Cable_Pulls
mwd= modify_word_docx


###################################
#  To store user inputs for number
#  of Files 
###################################
csv_file_list=[]
log_list=[]
model_no_names=[]
cap_names=[]
fw_no_names=[]
product_fnames=[]
vendor_names=[]
eco_names=[]
chassis_names=[]
cntrllr_names=[]

###################################
#  Questions / User Inputs
###################################
HP_dec = ui.hp_question() # HP drive or BB/SSD?
fw_type = ui.fw_type() #Qualification / Regression?

###################################
#  To make sure, User inputs enters  
#  a numeric character.
###################################
no_of_files='abc' #dummy string
while not no_of_files.isnumeric():
    no_of_files= input('\nPlease enter number of files'\
                        ' to concatenate: ')
    no_of_files.isnumeric()
no_of_files=int(no_of_files)

######################################
#  This loop will collect all inputs
#  from User, for specified number of 
#  files. And store it in List, which 
#  is used to process later. 
######################################

for nof in range(no_of_files):
    csv_file = input('Enter full file path of .csv file'\
                     ' for File # '+str(nof+1)+ ': ' )
    csv_file_list.append(csv_file)
    
    
    ###################################
    #  Strings which will qualify 
    #  User Inputs for Log Files. 
    ###################################
    raidfault_str= 'RaidFault'

    # get file path 
    while True:
            temp_log = input('\nPlease enter path of Raid Fault'\
                             ' zipped file: ' )
                             
            temp_log = str(temp_log).replace('"','') 
            #removing double quotes
            if raidfault_str in temp_log:
                break
            else:
                print('\nIt is not a Raid Fault file!')
    log_list.append(temp_log)
    
    #########################
    # Ask and check for a 
    # valid Model number.
    # It will also return
    # Model number's Capacity
    # Firmware, Vendor Name, 
    # ECO number, and Product
    # Name. 
    #########################
    [temp_model,
    temp_capacity,
    temp_fw,
    temp_vendor,
    temp_eco,
    temp_product_name] = ui.hdd_model(HP_dec) #model number
    
    model_no_names.append(temp_model) 
    # Appending or Making list to process later
    cap_names.append(temp_capacity)
    fw_no_names.append(temp_fw) 
    product_fnames.append(temp_product_name)
    vendor_names.append(temp_vendor)
    eco_names.append(temp_eco) 

    #########################
    # Chassis No. from a 
    # predefined list. 
    #########################
    chassis_no = ui.chassis_in(nof) #chassis number
    chassis_names.append(fd.chassis_list_d[int(chassis_no)])
    
    #########################
    # Controller No. from a 
    # predefined list. 
    #########################
    cntrller_no = ui.cntrller_in(nof)
    cntrllr_names.append(fd.cntrllr_list_d[int(cntrller_no)])
    
    
#########################
# Enter Word Template
#########################
word_file = ui.word_in()


###################
# start_time
###################
import time
start_time = time.time()


#########################################
#  Find list of Model Number and its 
#  Firmware with same Family Name.
#########################################
new_list= lf.find_model_fw(HP_dec, product_fnames)

if fd.fw_type_d[fw_type]=='Qualification':
    temp_fw_type='Initial release of'
else:
    temp_fw_type='Firmware regression for'

    
####################################
# Replace KEYWORDS in Word Template
####################################

fixed_dir=os.path.dirname(r''+str(word_file))
#Directory where template word file is situated
fixed_dir=str(fixed_dir).replace('"','') #removing double quotes

file_name=word_file[-(len(word_file)-len(fixed_dir)-1):]
part_no=file_name[:19] # Part no for Footer
rev_no=part_no[-1] # Revision no of the table


###########################
# FIND TODAY'S DATE 
###########################
date=time.strftime("%m/%d/%Y") 


###########################
# KEYWORDS to be replaced 
# in Word Template.
###########################
replaceText = {"INITIAL": str(temp_fw_type),
                "VENDOR" : str(vendor_names[0]),
                "MDLLIST" : new_list,
                "FWLIST": str(fw_no_names[0]),
                "MODEL" : str(model_no_names[0]),
                "FW": str(fw_no_names[0]),
                "DATE":str(date),
                "ECONUM":str(eco_names[0]),
                "PRODUCT":str(product_fnames[0]),
                "REV":str(rev_no)}
#                "RSLT":str(pass_fail_dec)}

replaceText_f = {"FOOTER":str(part_no)}

###########################
# So that we can change
# name for different tests.
###########################
test_name=' SFT Raid Fault Final Report'
if os.path.isfile(r''+str(fixed_dir)+'\\'+str(part_no)
                    +str(test_name)+'.docx'):
                    
    os.remove(r''+str(fixed_dir)+'\\'+str(part_no)
                +str(test_name)+'.docx')

if os.path.isfile(r''+str(fixed_dir)+'\\temp_doc.docx'):
    os.remove(r''+str(fixed_dir)+'\\temp_doc.docx')

  
mwd.Modify_Word_Docx(word_file,fixed_dir,part_no,replaceText
                    ,replaceText_f,test_name) 
                    #Modifying Word Document

if os.path.isfile(''+str(fixed_dir)+'\\temp_doc.docx'):
    os.remove(r''+str(fixed_dir)+'\\temp_doc.docx')

#####################################
# writing files to report 
#####################################
t_fw_type= fd.fw_type_d[fw_type]
  

[ c1_creation_data, c1_recreation_data, 
  c2_creation_data, c2_recreation_data] = gwrf.generate_final_report(rff, fixed_dir
                                                                    , part_no, test_name, no_of_files
                                                                    , csv_file_list, log_list
                                                                    , fw_no_names, chassis_names
                                                                    , cntrllr_names, t_fw_type)
                                                    
            
                

print('\nYour Report is ready!\n') 

os.chdir(r''+str(c_path))  

elapse_time =round((time.time() - start_time),2) # seconds
if elapse_time < 60 :
    print("\n\nElapsed time: %s seconds" % elapse_time )
else:
    print("\n\nElapsed time: %s minutes" % round(((time.time() - start_time)/60),2))

#####################################
#              END                  #
#####################################