#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Developed and tested on:

- Linux 18.04 LTS
- Windows 10
- Python 3.7 (Spyder)

@author: Nikola Knezevic
"""

import os
import time as TIME
import datetime
from collections import OrderedDict
import re
import sys


#################################### PARAMETERS ##############################################

# sleep time (in sec)
TIME_SLEEP=2

# ARGUMENTS 
arguments=sys.argv[1:]
# check num of arguments
if len(arguments)!=2:
    print ("Incorrect arguments. Please enter the correct arguments.\n")
    TIME.sleep(TIME_SLEEP)
    sys.exit()
# arguments
arg1=arguments[0]
arg2=arguments[1]
# check keynames in arguments
if ('files=' not in arg1) and ('files=' not in arg2):
    print ("Incorrect arguments. Please enter the correct arguments.\n")
    TIME.sleep(TIME_SLEEP)
    sys.exit()
if ('lines=' not in arg1) and ('lines=' not in arg2):
    print ("Incorrect arguments. Please enter the correct arguments.\n")
    TIME.sleep(TIME_SLEEP)
    sys.exit()
# take values of arguments
if 'files=' in arg1:
    arg1_data=re.sub('files=','',arg1)
    arg2_data=re.sub('lines=','',arg2)
else:
    arg1_data=re.sub('lines=','',arg1)
    arg2_data=re.sub('files=','',arg2)
    pom=arg1_data
    arg1_data=arg2_data
    arg2_data=pom
# list of files
arg1_data=arg1_data.split(',')
arg1_data[0]=re.sub('\[','',arg1_data[0])
arg1_data[-1]=re.sub('\]','',arg1_data[-1])
list_of_files=arg1_data
# list of lines for searching
arg2_data=arg2_data.split(',')
arg2_data=[re.sub('\[|\]','',x) for x in arg2_data]
arg2_data=[[float(arg2_data[i*2]),float(arg2_data[(i*2)+1])] 
           for i in range(int(len(arg2_data)/2))]
list_of_lines=arg2_data

# FOLDERS
# get current working directory
cwd=os.getcwd()
# directory of files
files_folder=os.path.join(cwd,'files_for_search')
# output directory
output_directory=os.path.join(cwd,'results')

# current datetime
current_date_time=(datetime.datetime.now()).strftime('_%Y%m%d_%H%M%S')

# header of a file
header=['atomic_num.ion_num','name','ionization','wavelength(Ang)',
        'relative_intensity','frac_of_max_rel_int','flags',
        'reference']

# number of tabs
num_of_tabs=len(header)-1

##############################################################################################


###################################### FUNCTIONS #############################################

# function that opens given file and retrieves data from it
def retrieve_file_data(filename):
    # file path
    file_path=os.path.join(files_folder,filename)
    # open and read file
    f=open(file_path,'r')
    data=f.read().splitlines()
    f.close()
    # take only rows that contain el lines
    data=[e for e in data if e.count('\t')==num_of_tabs]
    data=[e.split('\t') for e in data if e.split('\t')!=header]
    # sort data by atomic number - ionization level
    # and then by wawelength
    ANIL=[float(e[0]) for e in data]
    WL=[float(e[3]) for e in data]
    ELEMENTS=[e[1]+' '+e[2] for e in data]
    for i in range(len(data)):
        data[i].insert(0,ELEMENTS[i])
        data[i].insert(0,WL[i])
        data[i].insert(0,ANIL[i])
    data=sorted(data, key = lambda x: (x[0], x[1]))
    # elements
    elements=[e[2] for e in data]
    # wavelengths
    wavelengths=[e[1] for e in data]
    # rows
    rows=[e[3:] for e in data]
    # unique elements
    elements_unique=list(OrderedDict.fromkeys(elements))
    # wavelengths reorganised
    wavelengths=[[wavelengths[j] for j in range(len(elements)) 
                  if elements[j]==elements_unique[i]] 
                 for i in range(len(elements_unique))]
    # rows reorganised --> rows[i] is now list of lists..
    rows=[[rows[j] for j in range(len(elements)) 
           if elements[j]==elements_unique[i]] 
          for i in range(len(elements_unique))]
    # return data
    return elements_unique,wavelengths,rows

# function that looks inside given file and seeks 
# for a given line (within some range)
def serach_line_in_file(LINE,FILE):
    try:
        line=LINE
        lr=[line[0]-line[1],line[0]+line[1]]
        elements_unique,wavelengths,rows=retrieve_file_data(FILE)
        result=[]        
        for i in range(len(elements_unique)):
            element=elements_unique[i] # element
            WLS=wavelengths[i] # list
            ROWS=rows[i] # list of lists
            wavelen_around_line=[w for w in WLS if lr[0]<=w<=lr[1]]
            rows_around_line=[ROWS[j] for j in range(len(ROWS)) 
                              if lr[0]<=WLS[j]<=lr[1]]
            result.append([element,wavelen_around_line,rows_around_line])
        return result
    except Exception as e:
        print ("Something went wrong.\nError message:\n"
               +str(e)+"\nPlease check.\n")       
        TIME.sleep(TIME_SLEEP)
        return []

# main search function
def search(LINE,FILE):   
    line=LINE
    print ("* Looking for a line "+str(line[0])+" Ang ( +/- "+str(line[1])+" Ang ) inside "\
           +FILE+" file.\n")
    TIME.sleep(TIME_SLEEP)
    result=serach_line_in_file(line,FILE) 
    output=[]
    total_num=0
    if result!=[]:        
        for i in range(len(result)):           
            if result[i][1]!=[]:               
                num=len(result[i][1])                
                total_num=total_num+num                
                element=["Element: "+result[i][0]+"\n"]                
                element.append("Line: "+str(line[0])+" Ang ( +/- "+str(line[1])+" Ang )\n")
                element.append("Number of lines: "+str(num)+"\n\n")
                rows=result[i][2]
                rows=["\t".join(r)+"\n" for r in rows]
                rows.append("\n\n")
                output=output+element+rows
    if output!=[]:               
        msg="************ line "+str(line[0])+" Ang ( +/- "+str(line[1])+" Ang ) "\
            "inside "+FILE+" file ************"       
        output.insert(0,msg+"\n\n")
        output.insert(len(output),"TOTAL NUM OF LINES: "+str(total_num)+"\n")
        stars_len=len(msg)                 
        stars="*"*stars_len
        output.insert(len(output),stars+"\n\n\n")
    return output




##############################################################################################


######################################## PROGRAM #############################################

# result of a search
result=[]

# go trough list of files
for i in range(len(list_of_files)):
    # for every file
    filename=list_of_files[i]
    # go trough list of lines
    for j in range(len(list_of_lines)):
        # search for all lines in that file
        line=list_of_lines[j]
        output=search(line,filename)
        if output!=[]:
            result=result+output

# write everything to file
out_file="search_lines"+current_date_time+".txt"
if result!=[]:
    out_file_path=os.path.join(output_directory,out_file)
    f=open(out_file_path,'w')
    for i in range(len(result)):
        f.write(result[i])
    f.close()
    print ("FILE: "+out_file+" was successfully created.\n")
    TIME.sleep(TIME_SLEEP)
else:    
    print ("NO RESULTS AFTER SEARCH!\n")
    print ("FILE: "+out_file+" was not created.\n")
    TIME.sleep(TIME_SLEEP)

##############################################################################################




