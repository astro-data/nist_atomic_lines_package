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
from collections import OrderedDict
import time as TIME
from mendeleev import element
import roman
import sys
import re


######################################### PARAMETERS #########################################

# sleep time (in sec)
TIME_SLEEP=2

# ARGUMENTS 
arguments=sys.argv[1:]
arg1=arguments[0]
# check keyname in arguments
if ('files=' not in arg1):
    print ("Incorrect argument. Please enter the correct argument.\n")
    TIME.sleep(TIME_SLEEP)
    sys.exit()
# take values of arguments
arg1_data=re.sub('files=','',arg1)
# list of files
arg1_data=arg1_data.split(',')
arg1_data[0]=re.sub('\[','',arg1_data[0])
arg1_data[-1]=re.sub('\]','',arg1_data[-1])
list_of_files=arg1_data

# FOLDERS AND FILES
# get current working directory
cwd=os.getcwd()
# directory of files
files_folder=os.path.join(cwd,'files_for_search')
# output directory
output_directory=os.path.join(cwd,'results')
# file with elements and lines from WISeREP
wis_el_lines_file=os.path.join(cwd,'wis_el_and_lines.txt')

# border (for checking if line exists within border range)
border=1.0

# header of a file
header=['atomic_num.ion_num','name','ionization','wavelength(Ang)',
        'relative_intensity','frac_of_max_rel_int','flags',
        'reference']

# number of tabs
num_of_tabs=len(header)-1

##############################################################################################



######################################## FUNCTIONS ###########################################

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
    # unique elements
    elements_unique=list(OrderedDict.fromkeys(elements))
    # wavelengths reorganised
    wavelengths=[[wavelengths[j] for j in range(len(elements)) 
                  if elements[j]==elements_unique[i]] 
                 for i in range(len(elements_unique))]
    # return data
    return elements_unique,wavelengths

# function for checking if line exists in list of lines
def line_exists(listOflines,line):
    distance=[abs(listOflines[i]-line) for i in range(len(listOflines))]
    minDistance=min(distance)
    if minDistance <= border:
        return True
    else:
        return False

##############################################################################################



######################################### PROGRAM ############################################

# TAKE WISeREP ELEMENTS AND LINES
# open file and read elements and lines
f=open(wis_el_lines_file,'r')
data=f.read().splitlines()
f.close()
# rearrange data
data=[d.strip().split('=') for d in data if d.strip()!='']
# elements
wis_el=[d[0].strip().replace('_',' ') for d in data]
# lines
wis_lines=[(d[1].strip().replace('[','').replace(']','')).split(',') for d in data]
wis_lines=[[float(l[i].strip()) for i in range(len(l))] for l in wis_lines]
# element name
wis_el_name=[e.split()[0] for e in wis_el]
# element ionization level
wis_el_ion=[e.split()[1] for e in wis_el]
# atomic number of element
wis_el_atomic_num=[element(e).atomic_number for e in wis_el_name]
wis_el_atomic_num=['0'+str(e) if e in [1,2,3,4,5,6,7,8,9] else str(e) for e in wis_el_atomic_num]
# ion level of element
wis_el_ion_num=[roman.fromRoman(e) for e in wis_el_ion]
wis_el_ion_num=['0'+str(e-1) if e in [1,2,3,4,5,6,7,8,9,10] else str(e-1) for e in wis_el_ion_num]
# atomic_number.ion_level of element
wis_el_an_il=[wis_el_atomic_num[i]+'.'+wis_el_ion_num[i] for i in range(len(wis_el))]
wis_el_an_il_num=[float(e) for e in wis_el_an_il]
# wiserep flag
wis_flag='M'
# wiserep data
wis_data=[]
for i in range(len(wis_el)):
    for j in range(len(wis_lines[i])):
        wis_data.append([wis_el_an_il_num[i],wis_lines[i][j],wis_el[i],wis_el_an_il[i],
                         wis_el_name[i],wis_el_ion[i],str(wis_lines[i][j]),
                         'null','null',wis_flag,'wiserep'])
# sort elements and lines by atomic_num.ion_level and then wavelength
wis_data_sorted=sorted(wis_data, key = lambda x: (x[0], x[1]))

# go trough every file
for i in range(len(list_of_files)):
    print ("Checking for the missing WISeREP lines in the file: "+list_of_files[i]+"...\n")
    TIME.sleep(TIME_SLEEP)
    # missing lines
    MISSING_LINES=[]
    # retrieve data from the file
    file_el,file_lines=retrieve_file_data(list_of_files[i])
    # check if it's not empty file
    if file_el!=[]:
        # go trough all WISeREP el and their lines
        for j in range(len(wis_el)):       
            # checking first if WISeREP element exists in file
            if wis_el[j] not in file_el:
                # if not, take everything (all lines) for that element
                missing_lines=[e for e in wis_data_sorted if e[2]==wis_el[j]]              
                MISSING_LINES=MISSING_LINES+missing_lines              
            else:
                # else, check if specific lines are missing
                missing_lines=[e for e in wis_data_sorted if e[2]==wis_el[j] and 
                               line_exists(file_lines[file_el.index(wis_el[j])],e[1])==False]                               
                MISSING_LINES=MISSING_LINES+missing_lines
        # if there are missing lines, create file with missing lines
        if MISSING_LINES!=[]:
            print ("There are "+str(len(MISSING_LINES))+" missing lines in the file.\n")
            TIME.sleep(TIME_SLEEP)
            FILE_NAME="missing_wis_lines_in_"+list_of_files[i]
            FILE_PATH=os.path.join(output_directory,FILE_NAME)
            # sort again missing elements and lines by atomic_num.ion_level 
            # and then by wavelength
            MISSING_LINES=sorted(MISSING_LINES, key = lambda x: (x[0], x[1]))
            MISSING_LINES=[e[3:] for e in MISSING_LINES]
            MISSING_LINES.insert(0,header)
            # write to file
            f=open(FILE_PATH,'w')
            for r in MISSING_LINES:
                r_new="\t".join(r)+"\n"
                f.write(r_new)
            f.close()
            print ("File: "+FILE_NAME+" was created.\n\n")
            TIME.sleep(TIME_SLEEP)
        else:
            print ("There are no missing lines in the file.\n\n")
            TIME.sleep(TIME_SLEEP)
    else:
        print ("File: "+list_of_files[i]+" is empty!\n\n")
        TIME.sleep(TIME_SLEEP)

##############################################################################################



