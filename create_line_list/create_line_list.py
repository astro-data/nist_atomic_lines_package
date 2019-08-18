#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Developed and tested on:

- Linux 18.04 LTS
- Windows 10
- Python 3.7 (Spyder)

@author: Nikola Knezevic
"""

import time as TIME
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from mendeleev import element
import roman
import os
import sys
import datetime


############################################# PARAMETERS ###############################################

# url of element's table (GENERAL)
ELEMENTS_TABLE_URL='http://physics.nist.gov/cgi-bin/ASD/lines1.pl?spectra='\
                   '&low_w=&upp_wn=&upp_w=&low_wn=&unit=0&submit=Retrieve+Data'\
                   '&de=0&java_window=3&java_mult=&format=1&line_out=0&en_unit=0'\
                   '&output=0&bibrefs=1&page_size=15&show_obs_wl=1&show_calc_wl=1&'\
                   'order_out=0&max_low_enrg=&show_av=2&max_upp_enrg=&tsb_value=0&min_str=&'\
                   'A_out=0&intens_out=on&max_str=&allowed_out=1&forbid_out=1&min_accur=&'\
                   'min_intens=&conf_out=on&term_out=on&enrg_out=on&J_out=on'

# list of possible error messages from NIST
nist_errors=['Error Message:','No lines are available in ASD with the parameters selected',
             'UD is not a valid element symbol.','Unrecognized token.']

# wait time (in sec)
TIME_SLEEP=2

# the number of attempts
LOOP_NUM=10

# flag for lines retrieved from NIST
FLAG='NIST'

# current date and time
date=datetime.datetime.now().strftime('%Y%m%d')
time=datetime.datetime.now().strftime('%H%M%S')

# [% of data, fraction of max rel int, min rel int, lower wavelength, upper wavelength]
# NOTE: wavelengths are given in Ang
# default parameters values
# parameters_default_values=[0,0,0,0,0] # retrieve ALL lines for given element 
                                        # (e.g. Ca II) from NIST
parameters_default_values=[50,0.2,0,2000,10000] # some default value

# READ PARAMETERS
param=sys.argv
# file containing manually added lines
MAN_LINES_FILE='' 
# file containing list of elements
ELEMENTS_FILE=''
# flag for creating output [all, list, matlab] (if not specified output==all)
output='all'
# flag for searching library [True, False] (if not specified library==True)
library=True
# flag for checking if max relativ intensity should be taken as: 
# - max relative intenisty of the specified range of element's wavelengths
# - max relativ intensity of the whole element
# possible values are ['all','range'] (if not specified rel_int_flag==all)
rel_int_flag='all'
# check parameters
for i in range(len(param)):
    if 'MAN_LINES_FILE' in param[i]:
        MAN_LINES_FILE=param[i].replace('MAN_LINES_FILE=','')
    if 'ELEMENTS_FILE' in param[i]:
        ELEMENTS_FILE=param[i].replace('ELEMENTS_FILE=','')
    if 'output' in param[i]:
        output=param[i].replace('output=','')
        if output not in ['all','list','matlab']:
            output='all'
    if 'library' in param[i]:
        library=param[i].replace('library=','')
        if library.lower()=='true':
            library=True
        else:
            library=False
    if 'rel_int_flag' in param[i]:
        rel_int_flag=param[i].replace('rel_int_flag=','')
        if rel_int_flag not in ['all','range']:
            rel_int_flag='all'    
# if nothing was specified in parameters
if MAN_LINES_FILE=='' and ELEMENTS_FILE=='':
    print ('None of the files is specified as a parameter.')
    print ('Exiting program...\n')
    TIME.sleep(TIME_SLEEP)
    # exit program
    sys.exit()

# FOLDERS and FILES
# current working directory
cwd=os.getcwd()    
# folder for keeping lists of elements
list_of_elements_folder=os.path.join(cwd,'list_of_elements')
# folder for keeping lists of manually added lines
manually_added_lines_folder=os.path.join(cwd,'manually_added_lines')
# directory for script results 
data_directory=os.path.join(cwd,'script_results')
# NIST library folder
nist_library_folder=os.path.join(cwd,'NIST_ELEMENTS')
# list of all directories inside NIST library folder
nist_lib_folders=os.listdir(nist_library_folder)
nist_lib_folders_path=[os.path.join(nist_library_folder,e) 
                       for e in nist_lib_folders]
# list of all files inside NIST library (from all folders)
nist_lib_files=[os.listdir(e) for e in nist_lib_folders_path]
nist_lib_files_path=[[os.path.join(nist_lib_folders_path[i],nist_lib_files[i][j]) 
                      for j in range(len(nist_lib_files[i]))]
                     for i in range(len(nist_lib_folders_path))]
nist_lib_files=sum(nist_lib_files,[])
nist_lib_files_path=sum(nist_lib_files_path,[])

########################################################################################################


############################################### FUNCTIONS ##############################################

# download element table from NIST database e.g. Ca II 
def download_nist_el(nist_element,parameters,ri_flag):
    nist_element_plus=nist_element.replace(' ','+')
    print ('Downloading table for element '+nist_element+' from NIST database...\n')
    TIME.sleep(TIME_SLEEP)
    # check parameters for lower and upper wavelength
    lower=parameters[3]
    upper=parameters[4]
    # flag for checking WL
    if lower==0.0 and upper==0.0:
        check_wl=False
    else:
        check_wl=True
    # if we don't have range but (by mistake) we specified ri_flag=='range'
    # ---> we change ri_flag to 'all'
    if check_wl==False and ri_flag=='range':
        ri_flag='all'
    # flags
    network=False
    loop_num=0  
    while (network==False) and (loop_num<LOOP_NUM):
        try:
            with requests.Session() as s:
                # url of element's table for SPECIFIED element with given wavelengths
                url=ELEMENTS_TABLE_URL.replace('http://physics.nist.gov/cgi-bin/ASD/'\
                                               'lines1.pl?spectra=','http://physics.nist.gov/'\
                                               'cgi-bin/ASD/lines1.pl?spectra='+nist_element_plus)
                r=s.get(url)
                soup=BeautifulSoup(r.text,'lxml')
                # check for errors
                error=soup.findAll(text=nist_errors)               
                if error!=[]:
                    print ('No results in NIST database for element '+nist_element)                   
                    err=[str(er) for er in error if str(er)!='Error Message:']
                    if err!=[]:
                        print ('Error Message : '+err[0])
                    print ('\n')                   
                    TIME.sleep(TIME_SLEEP)
                    nistTable=[]
                    indication='null'
                    max_rel_int='null'
                    return nistTable,indication,max_rel_int
                table = soup.findAll('pre')
                res=(str(table[0])).splitlines()
                network=True
                print ('Table for element '+nist_element+' was successfully '\
                       'downloaded from NIST.\n')
                TIME.sleep(TIME_SLEEP)        
        except Exception as e:
            print ('Something went wrong while trying to download table for '\
                   'element '+nist_element+' from NIST.')
            print ('Error message:\n'+str(e))
            print ('Trying again ('+str(loop_num+1)+' out of '+str(LOOP_NUM)+')...\n')
            TIME.sleep(TIME_SLEEP)
            network=False
            loop_num=loop_num+1   
    # check if there is stil no data from NIST
    if loop_num==LOOP_NUM:
        print ('Unable to download table for element '+nist_element+'\n')
        TIME.sleep(TIME_SLEEP)
        nistTable=[]
        indication='null'
        max_rel_int='null'
        return nistTable,indication,max_rel_int
    # work with the downloaded data now
    try:
        print ('Extract and rearrange data from downloaded table.\n')
        TIME.sleep(TIME_SLEEP)
        # put data into lists
        data=[row.split('|') for row in res]
        # find positions of wavelength, rel. int. and ref.
        header_row=[d.strip() for d in data[2]]
        data_row=data[6]
        wave_ind=header_row.index('Observed')
        rel_int_ind=header_row.index('Rel.')
        ref_ind=len(data_row)-2
        # wavelength and rel. int.
        l=['' for i in range(len(res))]
        ri=['' for i in range(len(res))]
        for i in range(len(res)):
            if len(data[i])>1:
                l[i]=data[i][wave_ind].strip()
                ri[i]=data[i][rel_int_ind].strip()
        # take wawelength (in angstroms), relative intensity and reference
        wavelength=[]
        relativeIntensity=[]
        reference=[]    
        for i in range(len(res)):
            x=re.findall('\d+\.\d+',l[i])
            y=re.findall('\d+',ri[i])
            if x!=[] and y!=[] and float(y[0])!=0.0:
                wavelength.append(float(x[0]))
                relativeIntensity.append(float(y[0]))
                pom=re.findall('>[A-Za-z\d]+</a>',data[i][ref_ind].strip())
                if pom!=[]:
                    ref=re.sub('>|</a>','',pom[0])
                else:
                    ref=''
                reference.append(ref)
        # return relativeIntensity,wavelength,reference
        # this is sorted by relative intensity, and then by wavelength 
        # (wavelengths were sorted by default)
        # THIS TABLE IS EVERYTHING FOR THAT ELEMENT !!!
        nistTable=[[a,b,c] for (a,b,c) in sorted(zip(relativeIntensity,wavelength,reference), 
                   key=lambda pair: pair[0], reverse=True)]
        # if table is empty
        if nistTable==[]:
            print ('Downloaded NIST table for element '+nist_element+' is empty!\n')
            TIME.sleep(TIME_SLEEP)
            indication='null'
            max_rel_int='null'
            return nistTable,indication,max_rel_int
        else:            
            # remove duplicates
            df=pd.DataFrame(nistTable)
            df=df.drop_duplicates()
            nistTable=df.values.tolist()
            # if there are same lines with different relative int, then take line with the
            # highest relative intensity
            ind=[]
            for i in range(0,len(nistTable)-1):
                l=nistTable[i][1]
                if i not in ind:
                    for j in range(i+1,len(nistTable)):
                        l1=nistTable[j][1]
                        if l==l1:
                            ind.append(j)
            nistTable=[nistTable[i] for i in range(len(nistTable)) if i not in ind]
            #--------------------------------------------------------
            # keep everything
            nistTable_all=[e for e in nistTable]
            total_num=len(nistTable_all)
            #--------------------------------------------------------
            # max relative intensity if ri_flag=='all'
            if ri_flag=='all':
                max_rel_int=nistTable[0][0]
            # if we need to check WL
            if check_wl==True:
                if lower!=0.0 and upper!=0.0:
                    nistTable=[e for e in nistTable if e[1]>=lower and e[1]<=upper]
                elif lower!=0.0:
                    nistTable=[e for e in nistTable if e[1]>=lower]
                elif upper!=0.0:
                    nistTable=[e for e in nistTable if e[1]<=upper]         
                # check if table is empty        
                if nistTable==[]:
                    print ('Downloaded NIST table for element '+nist_element+' is empty!\n')
                    TIME.sleep(TIME_SLEEP)
                    indication='null'
                    max_rel_int='null'
                    return nistTable,indication,max_rel_int
            # nistTable is still sorted by relative intensity, and then by wavelength 
            # max of relative intensity if ri_flag=='range'
            if ri_flag=='range':
                max_rel_int=nistTable[0][0]
            # number of elements
            num_of_elements=len(nistTable)                           
            # percent of data
            percent_of_data=parameters[0]
            # fraction of max relative intensity
            fraction_of_max_rel_int=parameters[1]
            # minimun relative intensity value
            min_rel_int_value=parameters[2]
            # if there is a case of all zero parameters then return everything
            if percent_of_data==0.0 and fraction_of_max_rel_int==0.0 and min_rel_int_value==0.0:
                if check_wl==False:
                    indication='all'
                else:
                    indication='all_within_range'
                return nistTable,indication,max_rel_int
            else:
                # first ask if there is % of data and find all of those values
                if percent_of_data > 0.0:
                    # percent of data as number of elements
                    if ri_flag=='range':
                        num_of_data_after_percent=int(round((num_of_elements*percent_of_data)/100.0+0.5))
                        # case where I need to have at least 1 element, because I may have
                        # num_of_data_after_percent=int(round(0.5)) ---> 
                        # ----> it will be num_of_data_after_percent==0
                        # and I need to have at least 1 element (with the biggest rel. int.)
                        if num_of_data_after_percent==0:
                            num_of_data_after_percent=1
                        percent_table=[nistTable[i] for i in range(num_of_data_after_percent)]
                    else:
                        num_of_data_after_percent=int(round((total_num*percent_of_data)/100.0+0.5))
                        # case where I need to have at least 1 element, because I may have
                        # num_of_data_after_percent=int(round(0.5)) ---> 
                        # ----> it will be num_of_data_after_percent==0
                        # and I need to have at least 1 element (with the biggest rel. int.)
                        if num_of_data_after_percent==0:
                            num_of_data_after_percent=1
                        percent_table_all=[nistTable_all[i] for i in range(num_of_data_after_percent)]
                        percent_table=[e for e in nistTable if e in percent_table_all]
                    el_num_percent_table=len(percent_table)
                else:
                    percent_table=[]
                    el_num_percent_table=0
                # then ask if there is fraction of max relative intensity
                if fraction_of_max_rel_int > 0.0:     
                    # find all values within this fraction
                    fraction_table=[nistTable[i] for i in range(num_of_elements) 
                                    if nistTable[i][0] >= max_rel_int*fraction_of_max_rel_int]
                    el_num_fraction_table=len(fraction_table)
                else:
                    fraction_table=[]
                    el_num_fraction_table=0
                # ask if there is a min relative intensity value
                if min_rel_int_value > 0.0:
                    # find all values from this min value and above
                    minimum_table=[nistTable[i] for i in range(num_of_elements) 
                                   if nistTable[i][0] >= min_rel_int_value]
                    el_num_minimum_table=len(minimum_table)
                else:
                    minimum_table=[]
                    el_num_minimum_table=0
                # return table that has the most elements
                tables=[percent_table,fraction_table,minimum_table]
                len_tables=[el_num_percent_table,el_num_fraction_table,el_num_minimum_table]
                max_len=max(len_tables)                
                # if all tables are empty
                if max_len==0:
                    print ('Downloaded NIST table for element '+nist_element+' is empty!\n')
                    TIME.sleep(TIME_SLEEP)
                    nistTable=[]
                    indication='null'
                    max_rel_int='null'
                    return nistTable,indication,max_rel_int
                ind_of_max_len=len_tables.index(max_len)
                if check_wl==False:
                    indications=['percent_of_data','fraction_of_max_rel_int','min_rel_int']
                else:
                    indications=['percent_of_data_within_range','fraction_of_max_rel_int_within_range',
                                 'min_rel_int_within_range']            
                indication=indications[ind_of_max_len]
                return tables[ind_of_max_len],indication,max_rel_int    
    except Exception as e:
        print ('Something went wrong while trying to extract and rearrange data from the table.')
        print ('Error message:\n'+str(e)+'\n')
        TIME.sleep(TIME_SLEEP)
        nistTable=[]
        indication='null'
        max_rel_int='null'
        return nistTable,indication,max_rel_int

# function that creates table for element in specific format
def create_table(nist_element,parameters,ri_flag):
    elTable,indication,ri_max_val=download_nist_el(nist_element,parameters,ri_flag)
    if elTable!=[] and indication!='null' and ri_max_val!='null':
        elementName=nist_element.split()[0]
        elementIonization=nist_element.split()[1]      
        atomicNumber=element(elementName).atomic_number
        if atomicNumber in [1,2,3,4,5,6,7,8,9]:
            atomicNumber='0'+str(atomicNumber)
        else:
            atomicNumber=str(atomicNumber)
        ionizationNumber=roman.fromRoman(elementIonization)
        if ionizationNumber in [1,2,3,4,5,6,7,8,9,10]:
            ionizationNumber='0'+str(ionizationNumber-1)
        else:
            ionizationNumber=str(ionizationNumber-1)
        atomic_num_ion_num=atomicNumber+'.'+ionizationNumber       
        # this is sorted by relative intensity (because I downloaded element table like that)
        elTable=[[atomic_num_ion_num,elementName,elementIonization,elTable[i][1],
                  elTable[i][0],round(((100.0*elTable[i][0])/ri_max_val)/100.0,4),FLAG,
                  elTable[i][2]] for i in range(len(elTable))]
        # sort now by wavelength and return in format [[atomic_num.ion_num], [name], ...,
        # ..., [reference]]
        elTable=[[elTable[i][k] for i in range(len(elTable))] for k in range(len(elTable[0]))]
        elTable=[[a0,a1,a2,a3,a4,a5,a6,a7] for (a3,a0,a1,a2,a4,a5,a6,a7) in
                 sorted(zip(elTable[3],elTable[0],elTable[1],elTable[2],elTable[4],elTable[5],
                            elTable[6],elTable[7]), key=lambda pair: pair[0], reverse=False)]
        elTable=[[elTable[i][k] for i in range(len(elTable))] 
                 for k in range(len(elTable[0]))]
    return elTable,indication

# merge rows
def merge_rows(indexOfRow1,indexOfRow2,rData):
    # I don't choose line in nist if rt doesnt't exists for that line ot it is equal 0
    # and for manually I have null (null) if I don't know relative intensity
    rt1=rData[4][indexOfRow1]
    rt2=rData[4][indexOfRow2][0]
    if rt2 not in rt1:
        rData[4][indexOfRow1].append(rt2)
        rData[5][indexOfRow1].append(rData[5][indexOfRow2][0])
    # flags (posible many entries for manually)
    f1=[k.lower() for k in rData[6][indexOfRow1]]    
    f2=rData[6][indexOfRow2]
    for el in f2:
        if el.lower() not in f1:
            rData[6][indexOfRow1].append(el)
    # references (posible many entries for manually)
    r1=[k.lower() for k in rData[7][indexOfRow1]]    
    r2=rData[7][indexOfRow2]
    for el in r2:
        if el.lower() not in r1:
            rData[7][indexOfRow1].append(el)

# write list to file
def write_to_file(filename,listOfData):
    with open(filename, 'w') as f:
        for item in listOfData:
            f.write(item+'\n')

# check if to take or not flags and references from manually added lines
def check_man_flag_ref(wavelength,relativeIntensity,manuallyList):
    if wavelength in manuallyList[3]:
        position=manuallyList[3].index(wavelength)
        ri=manuallyList[4][position]
        if ri < relativeIntensity and str(ri)!='null':
            return False
    return True

# put relevant flags or references
def put_flag_ref(flags,wavelength,relativeIntensity,manuallyList,flagOrRef):
    # at the begining see if we work with flag or ref
    if flagOrRef=='flag':
        column=6
    else:
        column=7
    # if there are more than one flag in list of flags
    if len(flags) > 1:
        flags1=[]
        # ask if to take or not flags from manually added lines
        res=check_man_flag_ref(wavelength,relativeIntensity,manuallyList)
        if res==False: # don't take manuall flags and references
            position=manuallyList[3].index(wavelength)
            for i in range(len(flags)):
                flag=flags[i]
                if flag not in manuallyList[column][position] and flag!='':
                    flags1.append(flag)
            if flags1!=[]:
                return ";".join(e for e in flags1)
            else:
                return ''
        else: # return everything
            return ";".join(e for e in flags if e!='')
    else:
        # return everything
        return flags[0]

# function for rearranging data
def rearrange_data(Data,manuall_data,m):
    # add data to rearrange
    rearrangedData=Data
    rearrangedData[4]=[[rearrangedData[4][i]] for i in range((len(rearrangedData[4])))]
    rearrangedData[5]=[[rearrangedData[5][i]] for i in range((len(rearrangedData[5])))]
    rearrangedData[6]=[(rearrangedData[6][i]).split(';') for i in range((len(rearrangedData[6])))]
    rearrangedData[7]=[(rearrangedData[7][i]).split(';') for i in range((len(rearrangedData[7])))]
    # find duplicates of wavelengths
    waveDuplicates=list(set([x for x in rearrangedData[3] if rearrangedData[3].count(x) > 1]))
    # find indexes of repeated wavelengths
    waveDuplicatesIndices = [[i for i, x in enumerate(rearrangedData[3]) if x == k] 
                             for k in waveDuplicates]
    # rows for removing after merging duplicates
    removeRows=[]
    # now merge indices if they are for the same element
    for i in range(len(waveDuplicatesIndices)):
        throw=[]
        for j in range(len(waveDuplicatesIndices[i])-1):
            if j not in throw:
                for k in range(j+1,len(waveDuplicatesIndices[i])):
                    if k not in throw:
                        if (rearrangedData[0][waveDuplicatesIndices[i][j]]==
                            rearrangedData[0][waveDuplicatesIndices[i][k]]):
                            merge_rows(waveDuplicatesIndices[i][j],waveDuplicatesIndices[i][k],
                                      rearrangedData)
                            throw.append(k)
                            removeRows.append(waveDuplicatesIndices[i][k])
    # now remove rows that are duplicates
    rearrangedData=[[rearrangedData[k][i] for i in range(len(rearrangedData[k])) if i not in removeRows] 
                    for k in range(len(rearrangedData))]
    rearrangedData[4]=[max([e for e in rearrangedData[4][i] if e!='null']) 
                       if len(rearrangedData[4][i])>1 else rearrangedData[4][i][0] 
                       for i in range(len(rearrangedData[4]))]
    rearrangedData[5]=[max([e for e in rearrangedData[5][i] if e!='null']) 
                       if len(rearrangedData[5][i])>1 else rearrangedData[5][i][0] 
                       for i in range(len(rearrangedData[5]))]
    if m==True:
        rearrangedData[6]=[put_flag_ref(rearrangedData[6][i],rearrangedData[3][i],rearrangedData[4][i],
                           manuall_data,'flag') for i in range(len(rearrangedData[6]))]
        rearrangedData[7]=[put_flag_ref(rearrangedData[7][i],rearrangedData[3][i],rearrangedData[4][i],
                           manuall_data,'reference') for i in range(len(rearrangedData[7]))]
    else:
        rearrangedData[6]=[";".join(e for e in rearrangedData[6][i] if e!='') 
                           for i in range((len(rearrangedData[6])))]
        rearrangedData[7]=[";".join(e for e in rearrangedData[7][i] if e!='') 
                           for i in range((len(rearrangedData[7])))]
    # sort everyting by wavelengths
    wavelengths=rearrangedData[3]
    rearrangedData=[[y for (x,y) in sorted(zip(wavelengths,rearrangedData[k]), key=lambda 
                     pair: pair[0], reverse=False)] for k in range(len(rearrangedData))]
    # return result
    return rearrangedData

# read NIST library data
def read_nist_data(nist_data_file):
    # find full path
    ind=nist_lib_files.index(nist_data_file)
    full_path=nist_lib_files_path[ind]
    # open and read file
    f=open(full_path,'r')
    list_data=f.read().splitlines()
    f.close()
    list_data=[e.split('\t') for e in list_data]
    # return data
    return list_data

# function for searching NIST library
def search_nist_library(nist_element,parameters,ri_flag):
    nist_element_=nist_element.replace(' ','_')
    print ('Searching NIST library for the element '+nist_element+' ...\n')
    TIME.sleep(TIME_SLEEP)
    if nist_element_+'.dat' not in nist_lib_files:
        print ("Element "+nist_element+" doesn't exist in NIST library.\n")
        TIME.sleep(TIME_SLEEP)
        nistTable=[]
        indication='null'
        return nistTable,indication
    else:
        # read nist library data
        list_data=read_nist_data(nist_element_+'.dat')
        #------------------------------------------------------------------------------
        # map where are 'atomic_num.ion_num', 'name', 'ionization', 'wavelength(Ang)',
        # 'relative_intensity', 'frac_of_max_rel_int', 'flags', 'reference'
        anio_ind=list_data[0].index('atomic_num.ion_num')
        name_ind=list_data[0].index('name')
        ion_ind=list_data[0].index('ionization')
        wl_ind=list_data[0].index('wavelength(Ang)')
        ri_ind=list_data[0].index('relative_intensity')
        fmri_ind=list_data[0].index('frac_of_max_rel_int')
        flag_ind=list_data[0].index('flags')
        ref_ind=list_data[0].index('reference')       
        # now remove first row
        list_data=list_data[1:]        
        #******************************************************************************
        # keep everything
        list_data_all=list_data[1:]
        atomic_num_ion_num=[e[anio_ind] for e in list_data_all]
        name=[e[name_ind] for e in list_data_all]
        ionization=[e[ion_ind] for e in list_data_all]
        wavelength=[float(e[wl_ind]) for e in list_data_all]
        relativeIntensity=[float(e[ri_ind]) for e in list_data_all]
        fracOfMaxRelInt=[float(e[fmri_ind]) for e in list_data_all]
        flags=[e[flag_ind] for e in list_data_all]
        reference=[e[ref_ind] for e in list_data_all]
        # sort by relative intensity, and then by wavelength 
        # (wavelengths were sorted by default)
        list_data_all=[[c,d,e,b,a,f,g,h] for (a,b,c,d,e,f,g,h) in 
                       sorted(zip(relativeIntensity,wavelength,atomic_num_ion_num,name,
                                  ionization,fracOfMaxRelInt,flags,reference), 
                       key=lambda pair: pair[0], reverse=True)]
        # total number of elements
        total_num=len(list_data_all)
        #******************************************************************************       
        #------------------------------------------------------------------------------
        # check parameters for lower and upper wavelength
        lower=parameters[3]
        upper=parameters[4]
        # flags
        if lower==0.0:
            low_range=False
        else:
            low_range=True
        if upper==0.0:
            upp_range=False
        else:
            upp_range=True
        # change flag (if necessary)
        if low_range==False and upp_range==False and ri_flag=='range':
            ri_flag='all'
        # remove rows that don't belong to the WL range
        keep_rows=[]
        num_list_data_old=len(list_data)
        for i in range(len(list_data)):
            if low_range==True and upp_range==True:
                if float(list_data[i][wl_ind])>=lower and float(list_data[i][wl_ind])<=upper:
                    keep_rows.append(i)
            elif low_range==True:
                if float(list_data[i][wl_ind])>=lower:
                   keep_rows.append(i)
            elif upp_range==True:
                if float(list_data[i][wl_ind])<=upper:
                   keep_rows.append(i)
            else: # low_range==False and upp_range==False
                keep_rows.append(i)
        list_data=[list_data[i] for i in range(len(list_data)) if i in keep_rows]
        # check if the list is empty after removing rows
        if list_data==[]:
            print ('Retrieved table for the element '+nist_element+' is empty!\n')
            TIME.sleep(TIME_SLEEP)
            nistTable=[]
            indication='null'
            return nistTable,indication
        #-----------------------------------------------------------------------------
        atomic_num_ion_num=[e[anio_ind] for e in list_data]
        name=[e[name_ind] for e in list_data]
        ionization=[e[ion_ind] for e in list_data]
        wavelength=[float(e[wl_ind]) for e in list_data]
        relativeIntensity=[float(e[ri_ind]) for e in list_data]
        # if some rows are removed and ri_flag=='range' I need to recalculate 
        # max. rel. int. within new range 
        if num_list_data_old!=len(keep_rows) and ri_flag=='range':
            ri_max_val=max(relativeIntensity) 
            fracOfMaxRelInt=[round(((100.0*e)/ri_max_val)/100.0,4) for e in relativeIntensity]
        else:
            fracOfMaxRelInt=[float(e[fmri_ind]) for e in list_data]
        flags=[e[flag_ind] for e in list_data]
        reference=[e[ref_ind] for e in list_data]
        # sort by relative intensity, and then by wavelength 
        # (wavelengths were sorted by default)
        list_data=[[c,d,e,b,a,f,g,h] for (a,b,c,d,e,f,g,h) in 
                   sorted(zip(relativeIntensity,wavelength,atomic_num_ion_num,name,
                              ionization,fracOfMaxRelInt,flags,reference), 
                   key=lambda pair: pair[0], reverse=True)]
        # number of elements
        num_of_elements=len(list_data)
        #-----------------------------------------------------------------------------       
        # now check parameters
        # percentage of data
        percent_of_data=parameters[0]
        # first ask if there is % of data and find all of those values
        if percent_of_data > 0.0:
            # percent of data as number of elements
            if ri_flag=='range':
                num_of_data_after_percent=int(round((num_of_elements*percent_of_data)/100.0+0.5))
                # case where I need to have at least 1 element, because I may have
                # num_of_data_after_percent=int(round(0.5)) ---> 
                # ----> it will be num_of_data_after_percent==0
                # and I need to have at least 1 element (with the biggest rel. int.)
                if num_of_data_after_percent==0:
                    num_of_data_after_percent=1
                percent_table=[list_data[i] for i in range(num_of_data_after_percent)]
            else:
                num_of_data_after_percent=int(round((total_num*percent_of_data)/100.0+0.5))
                # case where I need to have at least 1 element, because I may have
                # num_of_data_after_percent=int(round(0.5)) ---> 
                # ----> it will be num_of_data_after_percent==0
                # and I need to have at least 1 element (with the biggest rel. int.)
                if num_of_data_after_percent==0:
                    num_of_data_after_percent=1
                percent_table_all=[list_data_all[i] for i in range(num_of_data_after_percent)]
                percent_table=[e for e in list_data if e in percent_table_all]
            el_num_percent_table=len(percent_table)
        else:
            percent_table=[]
            el_num_percent_table=0
        # fraction of max relative intensity
        fraction_of_max_rel_int=parameters[1]
        # ask if there is fraction of max relative intensity
        if fraction_of_max_rel_int > 0.0:     
            # find all values within this fraction
            fraction_table=[list_data[i] for i in range(num_of_elements) 
                            if list_data[i][fmri_ind] >= fraction_of_max_rel_int]
            el_num_fraction_table=len(fraction_table)
        else:
            fraction_table=[]
            el_num_fraction_table=0       
        # minimun relative intensity value
        min_rel_int_value=parameters[2]             
        # ask if there is a min relative intensity value
        if min_rel_int_value > 0.0:
            # find all values from this min value and above
            minimum_table=[list_data[i] for i in range(num_of_elements) 
                           if list_data[i][ri_ind] >= min_rel_int_value]
            el_num_minimum_table=len(minimum_table)
        else:
            minimum_table=[]
            el_num_minimum_table=0        
        # if there is a case of all zero parameters then return everything
        if percent_of_data==0.0 and fraction_of_max_rel_int==0.0 and min_rel_int_value==0.0:
            if lower==0.0 and upper==0.0:
                indication='all'
            else:
                indication='all_within_range'
            nistTable=list_data
            print ('Table for the element '+nist_element+' was successfully retrieved.\n')
            TIME.sleep(TIME_SLEEP)
            return nistTable,indication  
        # return table that has the most elements
        tables=[percent_table,fraction_table,minimum_table]
        len_tables=[el_num_percent_table,el_num_fraction_table,el_num_minimum_table]
        max_len=max(len_tables)
        # if all tables are empty
        if max_len==0:
            print ('Retrieved table for the element '+nist_element+' is empty!\n')
            TIME.sleep(TIME_SLEEP)
            nistTable=[]
            indication='null'
            return nistTable,indication
        ind_of_max_len=len_tables.index(max_len)
        if lower==0.0 and upper==0.0:
            indications=['percent_of_data','fraction_of_max_rel_int','min_rel_int']
        else:
            indications=['percent_of_data_within_range','fraction_of_max_rel_int_within_range',
                         'min_rel_int_within_range']            
        indication=indications[ind_of_max_len]
        print ('Table for the element '+nist_element+' was successfully retrieved.\n')
        TIME.sleep(TIME_SLEEP)
        return tables[ind_of_max_len],indication

# function that creates table for element found in NIST library
def create_lib_table(nist_element,parameters,ri_flag):
    elTable,indication=search_nist_library(nist_element,parameters,ri_flag)
    if elTable!=[] and indication!='null':
        # this is sorted by relative intensity (because I downloaded element table like that)
        # sort now by wavelength and return in format [[atomic_num.ion_num], [name], ...,
        # ..., [reference]]
        elTable=[[elTable[i][k] for i in range(len(elTable))] for k in range(len(elTable[0]))]
        elTable=[[a0,a1,a2,a3,a4,a5,a6,a7] for (a3,a0,a1,a2,a4,a5,a6,a7) in
                 sorted(zip(elTable[3],elTable[0],elTable[1],elTable[2],elTable[4],elTable[5],
                            elTable[6],elTable[7]), key=lambda pair: pair[0], reverse=False)]
        elTable=[[elTable[i][k] for i in range(len(elTable))] 
                 for k in range(len(elTable[0]))]
    return elTable,indication

########################################################################################################


############################################### PROGRAM ################################################

# READING LIST OF MANUALLY ADDED LINES
# if manually added lines file was not specified as a parameter
if  MAN_LINES_FILE=='':
    manually=[]
    melan=[]
    mtitles=[]
else:
    # manually added lines file path
    manually_added_lines_file_path=os.path.join(manually_added_lines_folder,
                                                MAN_LINES_FILE)
    # read manually added lines file
    with open(manually_added_lines_file_path,'r') as f:
        manually=f.readlines()
    manually=[manually[i] for i in range(len(manually)) if manually[i].count('\t')==7]
    if len(manually)>1:
        manually=[manually[i].split('\t') for i in range(1,len(manually))]
        manually=[[manually[i][k].rstrip() for i in range(len(manually))] 
                  for k in range(len(manually[0]))]
        manually[3]=[float(manually[3][i]) for i in range(len(manually[3]))]
        manually[4]=[float(manually[4][i]) if manually[4][i].lower()!='null' else 'null' 
                     for i in range(len(manually[4]))]
        manually[5]=[float(manually[5][i]) if manually[5][i].lower()!='null' else 'null' 
                     for i in range(len(manually[5]))]
    else:
        manually=[]
# sort manually added lines because data will be sort
if manually!=[]:
    melan=manually[0]
    melan=list(set(melan))
    mtitles=[manually[1][manually[0].index(a)]+' '+manually[2][manually[0].index(a)] for a in melan]
    mel=[float(melan[i]) for i in range(len(melan))]
    melan=[y for (x,y) in sorted(zip(mel,melan), key=lambda pair: pair[0], reverse=False)]
    mtitles=[y for (x,y) in sorted(zip(mel,mtitles), key=lambda pair: pair[0], reverse=False)]
else:
    melan=[]
    mtitles=[]

# READING LIST OF ELEMENTS
# if list of elements file was not specified as a parameter
if  ELEMENTS_FILE=='':
    data=[]
    titles=[]
    elan=[]
else:
    # list of elements file path
    list_of_elements_file_path=os.path.join(list_of_elements_folder,
                                            ELEMENTS_FILE)
    # take list of elements
    with open(list_of_elements_file_path,'r') as f:
        liOfEl=f.readlines()
    liOfEl=[(x.rstrip()).split() for x in liOfEl if x.rstrip()!='']
    for i in range(len(liOfEl)):
        xx=liOfEl[i][0]+' '+liOfEl[i][1]
        if len(liOfEl[i])<3:
            yy=[float(x) for x in parameters_default_values]
        else:
            pom=(re.sub('\[|]','',liOfEl[i][2])).split(',')
            yy=[float(pom[0]),float(pom[1]),float(pom[2]),float(pom[3]),float(pom[4])]
        liOfEl[i]=[xx,yy]
    # now download/search data and put everything into lists
    data=[]
    titles=[]
    elan=[]
    par=['percent_of_data','fraction_of_max_rel_int','min_rel_int']
    parr=['percent_of_data_within_range','fraction_of_max_rel_int_within_range',
          'min_rel_int_within_range']
    par1=['% of data from maximum relative intensity',' fraction of maximum relative intensity',' of relative intensity']
    parr1=['% of data from maximum relative intensity within specified range',
           ' fraction of maximum relative intensity within specified range',
           ' of relative intensity within specified range']
    # go trough every element in the list
    for i in range(len(liOfEl)):
        # e.g. ['H I', [50.0, 0.2, 0.0, 2000.0, 10000.0]]
        el=liOfEl[i]
        # e.g. ['H', 'I']
        nameel=el[0].split()
        # e.g. 01.00
        an=element(nameel[0]).atomic_number
        if an in [1,2,3,4,5,6,7,8,9]:
            an='0'+str(an)
        else:
            an=str(an)
        ionn=roman.fromRoman(nameel[1])
        if ionn in [1,2,3,4,5,6,7,8,9,10]:
            ionn='0'+str(ionn-1)
        else:
            ionn=str(ionn-1)
        an_ionn=an+'.'+ionn
        # e.g. 'H I'
        elName=el[0]
        # e.g. [50.0, 0.2, 0.0, 2000.0, 10000.0]
        elPar=el[1]
        # create table
        if library==True:
            d,ind=create_lib_table(elName,elPar,rel_int_flag)
        else:
            d,ind=create_table(elName,elPar,rel_int_flag)       
        #---------------------------------------------------------------------
        if elPar[3]==0.0 and elPar[4]==0.0 and rel_int_flag=='range':
            rel_int_flag='all'        
        if rel_int_flag=='all':
            max_ri_msg="\nFor maximum rel. intensity of the element, "\
                       "the maximum rel. intensity for all element "\
                       "lines was taken."
        else:
            max_ri_msg="\nFor maximum rel. intensity of the element, "\
                       "the maximum rel. intensity for specified range of "\
                       "element lines was taken."
        #---------------------------------------------------------------------      
        if d!=[] and ind!='null':
            num=len(d[0])
            if ind!='all' and ind!='all_within_range':
                if ind in par:
                    Index=par.index(ind)            
                    if Index!=2:
                        title='Element : '+elName+max_ri_msg+'\nLines that are taken from NIST represent '\
                              +str(elPar[Index])+par1[Index]+' ('+str(num)+' lines from NIST).'
                    else:
                        title='Element : '+elName+max_ri_msg+'\nLines that are taken from NIST represent values '\
                              'above '+str(elPar[Index])+par1[Index]+' ('+str(num)+' lines from NIST).'
                else:
                    Index=parr.index(ind)
                    if Index!=2:
                        title='Element : '+elName+max_ri_msg+'\nLines that are taken from NIST represent '\
                              +str(elPar[Index])+parr1[Index]+' between '+str(elPar[3])+' - '\
                              +str(elPar[4])+' Ang ('+str(num)+' lines from NIST).'
                    else:
                        title='Element : '+elName+max_ri_msg+'\nLines that are taken from NIST represent values '\
                              'above '+str(elPar[Index])+parr1[Index]+' between '+str(elPar[3])+' - '\
                              +str(elPar[4])+' Ang ('+str(num)+' lines from NIST).'        
            else:
                if ind=='all':
                    title='Element : '+elName+max_ri_msg+'\nLines that are taken from NIST represent 100% of data '\
                          'from NIST ('+str(num)+' lines from NIST).'
                else:
                    title='Element : '+elName+max_ri_msg+'\nLines that are taken from NIST represent 100% of data '\
                          'from NIST within specified range between '+str(elPar[3])+' - '\
                          +str(elPar[4])+' Ang ('+str(num)+' lines from NIST).'
            data.append(d)
            titles.append(title)
            elan.append(an_ionn)
    # sort because data will be sort
    elan_float=[float(elan[i]) for i in range(len(elan))]
    elan=[y for (x,y) in sorted(zip(elan_float,elan), key=lambda pair: pair[0], reverse=False)]
    titles=[y for (x,y) in sorted(zip(elan_float,titles), key=lambda pair: pair[0], reverse=False)]

# CREATING LIST OF LINES
# flag to check if files of general lines AND manually added lines are empty
empty=False
# if there is a data
if data!=[]:    
    # rearrange data
    rearrData=[[data[i][k][j] for i in range(len(data)) for j in range(len(data[i][k]))] 
               for k in range(len(data[0]))]    
    # if there are manually added lines
    if manually!=[]:
        manuallyData=rearrange_data(manually,'No',False)
        # add manually to rearranged data
        rearrData=[rearrData[i]+manuallyData[i] for i in range((len(rearrData)))]
        # now rearrange everything again
        rearrangedData=rearrange_data(rearrData,manuallyData,True)
    else:
        # just rearrange data
        rearrangedData=rearrange_data(rearrData,'No',False)
    # now sort rearranged data by atomic_number.ion_number
    values=[float(rearrangedData[0][i]) for i in range(len(rearrangedData[0]))]
    sortedData=[rearrangedData[0][i]+'\t'+rearrangedData[1][i]+'\t'+rearrangedData[2][i]+'\t'+
          str(rearrangedData[3][i])+'\t'+str(rearrangedData[4][i])+'\t'+str(rearrangedData[5][i])+'\t'
          +rearrangedData[6][i]+'\t'+rearrangedData[7][i] for i in range(len(rearrangedData[0]))]
    nistTable=[y for (x,y) in sorted(zip(values,sortedData), key=lambda pair: pair[0], reverse=False)]
    justAN=[nistTable[i][0:5] for i in range(len(nistTable))]
    indices=[[i for i, x in enumerate(justAN) if x==y] for y in elan]
    indices=[min(x) for x in indices]
    mindices_out=[melan[i] for i in range(len(melan)) if melan[i] not in elan]
    mtitles_out=['Element : '+mtitles[i]+'\nOnly manually added lines for this element.' 
                for i in range(len(melan)) if melan[i] not in elan]
    mindices_out=[justAN.index(x) for x in mindices_out]    
    indices=indices+mindices_out
    titles=titles+mtitles_out    
    titles=[y for (x,y) in sorted(zip(indices,titles), key=lambda pair: pair[0], reverse=False)]
    indices=sorted(indices)
    elnum=[justAN.count(justAN[a]) for a in indices]
    titles=[titles[i]+'\nTotal number of lines : '+str(elnum[i]) for i in range(len(elnum))]
    titles=['\n'+a+'\n' for a in titles]
    for i in range(len(indices)):
        nistTable.insert(indices[i]+i,titles[i])
    # NIST list
    nistList=['atomic_num.ion_num\tname\tionization\twavelength(Ang)\trelative_intensity\t'+
              'frac_of_max_rel_int\tflags\treference']
    nistList.append('')
    nits=nistList+nistTable
    nits.append('')
    nits.append('TOTAL NUMBER OF ALL LINES : '+str(sum(elnum)))
    nits.append('')
    if output in ['all','list']: 
        # write NIST list to file
        write_to_file(os.path.join(data_directory,'list_of_lines_'+date+'_'+time+'.txt'),nits)   
        print ('File list_of_lines_'+date+'_'+time+'.txt was successfully created!')
        print ("\n")
        TIME.sleep(TIME_SLEEP)
elif manually!=[]:   
    rearrangedData=rearrange_data(manually,'No',False)   
    # now sort rearranged data by atomic_number.ion_number
    values=[float(rearrangedData[0][i]) for i in range(len(rearrangedData[0]))]
    sortedData=[rearrangedData[0][i]+'\t'+rearrangedData[1][i]+'\t'+rearrangedData[2][i]+'\t'+
          str(rearrangedData[3][i])+'\t'+str(rearrangedData[4][i])+'\t'+str(rearrangedData[5][i])+'\t'
          +rearrangedData[6][i]+'\t'+rearrangedData[7][i] for i in range(len(rearrangedData[0]))]
    nistTable=[y for (x,y) in sorted(zip(values,sortedData), key=lambda pair: pair[0], reverse=False)]
    justAN=[nistTable[i][0:5] for i in range(len(nistTable))]
    indices=[[i for i, x in enumerate(justAN) if x==y] for y in elan]
    indices=[min(x) for x in indices]    
    mindices_out=[melan[i] for i in range(len(melan)) if melan[i] not in elan]
    mtitles_out=['Element : '+mtitles[i]+'\nOnly manually added lines for this element.' 
                for i in range(len(melan)) if melan[i] not in elan]    
    mindices_out=[justAN.index(x) for x in mindices_out]    
    indices=indices+mindices_out
    titles=titles+mtitles_out    
    titles=[y for (x,y) in sorted(zip(indices,titles), key=lambda pair: pair[0], reverse=False)]
    indices=sorted(indices)
    elnum=[justAN.count(justAN[a]) for a in indices]
    titles=[titles[i]+'\nTotal number of lines : '+str(elnum[i]) for i in range(len(elnum))]
    titles=['\n'+a+'\n' for a in titles]
    for i in range(len(indices)):
        nistTable.insert(indices[i]+i,titles[i])
    # NIST list
    nistList=['atomic_num.ion_num\tname\tionization\twavelength(Ang)\trelative_intensity\t'+
      'frac_of_max_rel_int\tflags\treference']
    nistList.append('')
    nits=nistList+nistTable
    nits.append('')
    nits.append('TOTAL NUMBER OF ALL LINES : '+str(sum(elnum)))
    nits.append('')
    if output in ['all','list']:
        # write NIST list to file
        write_to_file(os.path.join(data_directory,'list_of_lines_'+date+'_'+time+'.txt'),nits)    
        print ('File list_of_lines_'+date+'_'+time+'.txt was successfully created!')
        print ("\n")
        TIME.sleep(TIME_SLEEP)
else:
    empty=True
    if output in ['all','list']:
        print ('File list_of_lines_'+date+'_'+time+'.txt was not created '\
               'because '+ELEMENTS_FILE+' and '+MAN_LINES_FILE+' files are empty!')
        print ("\n")
        TIME.sleep(TIME_SLEEP)

# CREATING MATLAB FILE
if (output in ['all','matlab']) and (empty==False):
    # write everything into matlab format
    # headers
    headers=[]
    indices=[]
    # matlab arrays
    arrays=[]
    for i in range(len(nistTable)):
        if 'Element' in nistTable[i]:
            hed=nistTable[i].split('\n')[1:len(nistTable[i].split('\n'))-1]
            hed=['% '+h+'\n' for h in hed]
            H=''
            for j in range(len(hed)):
                H=H+hed[j]
            headers.append(H)
            indices.append(i)
    for i in range(len(indices)):
        if i!=len(indices)-1:
            el_wavelengths=nistTable[indices[i]+1:indices[i+1]]
            wavelen=[e.split('\t')[3] for e in el_wavelengths]
            EL=el_wavelengths[0].split('\t')[1].lower()+el_wavelengths[0].split('\t')[2].lower()+'lines'
            WL=wavelen[0]
            for j in range(1,len(wavelen)):
                WL=WL+' '+wavelen[j]
            array=EL+'=['+WL+'];'    
            arrays.append(array)
        else:
            el_wavelengths=nistTable[indices[i]+1:]
            wavelen=[e.split('\t')[3] for e in el_wavelengths]
            EL=el_wavelengths[0].split('\t')[1].lower()+el_wavelengths[0].split('\t')[2].lower()+'lines'
            WL=wavelen[0]
            for j in range(1,len(wavelen)):
                WL=WL+' '+wavelen[j]
            array=EL+'=['+WL+'];'    
            arrays.append(array)
    # write to file in MATLAB format
    matlab_file='MATLAB_file_'+date+'_'+time+'.txt'
    with open(os.path.join(data_directory,matlab_file), 'w') as f:
        for i in range(len(headers)):
            f.write(headers[i]+'\n')
            f.write(arrays[i]+'\n')
            f.write('\n')
        f.write('\n')
        f.write('% TOTAL NUMBER OF ALL LINES : '+str(sum(elnum)))
        f.write('\n')
        f.write('\n')
    print ('File '+matlab_file+' was successfully created!')
    print ("\n")
    TIME.sleep(TIME_SLEEP)
else:
    if (empty==True) and (output in ['all','matlab']):
        matlab_file='MATLAB_file_'+date+'_'+time+'.txt'
        print ('File '+matlab_file+' was not created '\
               'because '+ELEMENTS_FILE+' and '+MAN_LINES_FILE+' files are empty!')
        print ("\n")
        TIME.sleep(TIME_SLEEP)

########################################################################################################


