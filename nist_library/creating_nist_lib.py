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
import requests
from bs4 import BeautifulSoup
import re
import sys
import roman
import pandas as pd
import shutil
import datetime
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header


##############################################################################################
######################################### PARAMETERS #########################################

# NIST Atomic Spectra Database URL-s
URL_TABLE='https://physics.nist.gov/cgi-bin/ASD/lines_pt.pl'
URL_ELEMENT='https://physics.nist.gov/cgi-bin/ASD/lines_hold.pl?el='

# url of element's table (GENERAL)
ELEMENTS_TABLE_URL='http://physics.nist.gov/cgi-bin/ASD/lines1.pl?spectra='\
                   '&low_w=&upp_wn=&upp_w=&low_wn=&unit=0&submit=Retrieve+Data'\
                   '&de=0&java_window=3&java_mult=&format=1&line_out=0&en_unit=0'\
                   '&output=0&bibrefs=1&page_size=15&show_obs_wl=1&show_calc_wl=1&'\
                   'order_out=0&max_low_enrg=&show_av=2&max_upp_enrg=&tsb_value=0&min_str=&'\
                   'A_out=0&intens_out=on&max_str=&allowed_out=1&forbid_out=1&min_accur=&'\
                   'min_intens=&conf_out=on&term_out=on&enrg_out=on&J_out=on'

# wait time (in sec)
TIME_SLEEP=2

# the number of attempts
LOOP_NUM=10

# file containing everything that exist in NIST 
# all elements (with their levels of ionization)
nist_filename='NIST_all_el_and_their_ion.txt'

# folder containing elements
elements_folder='NIST_ELEMENTS'

# list of possible error messages from NIST
nist_errors=['Error Message:','No lines are available in ASD with the parameters selected',
             'UD is not a valid element symbol.','Unrecognized token.']

# flag for lines retrieved from NIST
flag='NIST'

# current datetime
startTime=datetime.datetime.now()
currentDateTime=(startTime).strftime('[Date: %Y-%m-%d Time: %H:%M:%S]')

#------------------------------ email parameters -----------------------------------
# NOTE: SCRIPT ACCEPTS EITHER GMAIL (@gmail.com) 
#       OR WEIZMANN ACCOUNT (@weizmann.ac.il)
# email sender
mail_from="**********@gmail.com"
# email password
email_pass="**********"
# from prefix
from_prefix="[NIST SCRIPT ALARM]"
# recipents
mail_to=["**********@gmail.com"]
mail_cc=[]
# email subject
subject="Creating NIST library error"
# email body
email_body="An error occurred while executing the script "\
           +str(os.path.basename(sys.argv[0]))+" on "+currentDateTime+".\n\n"\
           "Please check what went wrong."
#-----------------------------------------------------------------------------------

##############################################################################################
##############################################################################################


##############################################################################################
######################################### FUNCTIONS ##########################################

# function for sending emails as alerts
def send_email(fromEmail,fromPrefix,password,toEmail,ccEmail,subject,body):
    print ('++++++++++++++++++++++++ Sending Email ++++++++++++++++++++++++')
    try:
        # choosing which server to use for sending e-mail
        # GMAIL or WEIZMANN
        if '@weizmann.ac.il' in fromEmail:
            eflag=True
        else:
            eflag=False
        #message
        message=MIMEText(body)
        message['Subject']=subject
        #message['From']=fromEmail
        message['From']=formataddr((str(Header(fromPrefix, 'utf-8')), fromEmail))
        message['To']=", ".join(toEmail)
        message['Cc']=", ".join(ccEmail)
        #server for sending message
        if eflag==False:
            server=smtplib.SMTP('smtp.gmail.com',587)
        else:
            server=smtplib.SMTP('doar.weizmann.ac.il')
        server.ehlo()
        if eflag==False:
            server.starttls()
            server.login(fromEmail,password)
        server.sendmail(fromEmail, toEmail+ccEmail, message.as_string())
        server.quit()        
        print ('Email sent!')
        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    except Exception as e:
        print ('Something went wrong while trying to send email!')
        print ('Error message : \n'+str(e))
        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

# exit program
def exit_program():
    # send email
    send_email(mail_from,from_prefix,email_pass,mail_to,mail_cc,subject,email_body)
    TIME.sleep(TIME_SLEEP)
    print ("\nExiting program...\n")
    TIME.sleep(TIME_SLEEP)
    endTime=datetime.datetime.now()
    executionTime=endTime-startTime
    print ('######################## Total execution time of the script ---> '
           +str(executionTime)+' #########################')
    print ('\n\n')
    sys.exit()

# function that retrieves all elements (with their levels of ionization) from NIST database
def retrive_elem_and_ions():
    # all elements
    elements=[]
    # atomic numbers of elements
    atomic_num_of_el=[]
    # elements with their ionizations (list of lists)
    elements_with_ion=[]
    # elements with their ionizations (single list)
    elements_all=[]
    print ('Obtaining table of elements (with their levels of ionization) '\
           'that exist in NIST...\n')
    TIME.sleep(TIME_SLEEP)
    # flags
    network=False
    loop_num=0    
    while (network==False) and (loop_num<LOOP_NUM):        
        try: 
            with requests.Session() as s:
                r=s.get(URL_TABLE)
                soup=BeautifulSoup(r.text,'lxml')
                tables=soup.findAll('table')
                table=tables[1].findAll('td')
                table_el=[re.findall('id="[A-Za-z]+"',str(t))[0] 
                          for t in table if re.findall('id="[A-Za-z]+"',str(t))!=[]]
                table_el=[re.sub('"|id=','',t) for t in table_el]
                elements=table_el
                table_a=[re.findall('<sup>\d+</sup>',str(t))[0] 
                         for t in table if re.findall('id="[A-Za-z]+"',str(t))!=[]]
                table_a=[re.sub('</?sup>','',t) for t in table_a]
                table_a=[t if int(t)>9 else '0'+t for t in table_a]
                atomic_num_of_el=table_a
                network=True
                #--------------------------------------------------------------------------
                #--------------------------------------------------------------------------
                # go trough every element and check for ionization
                for i in range(len(table_el)):
                    url_el=URL_ELEMENT+table_el[i]               
                    # flags
                    network1=False
                    loop_num1=0                   
                    while (network1==False) and (loop_num1<LOOP_NUM):                    
                        try:
                           with requests.Session() as s1:
                               r1=s1.get(url_el)
                               soup1=BeautifulSoup(r1.text,'lxml')
                               tables1=soup1.findAll('table')
                               table1=tables1[1].findAll('b')
                               table1=[re.findall('>[A-Za-z\s]+</a>',str(x))[0] 
                                       for x in table1 
                                       if re.findall('>[A-Za-z\s]+</a>',str(x))!=[]]
                               table1=[re.sub('>|</a>','',x) for x in table1]
                               elements_with_ion.append(table1)
                               elements_all=elements_all+table1
                               network1=True
                        except Exception as e1:
                            print ('Something went wrong while trying to find levels of '\
                                   'ionization that exist in NIST for element : '
                                   +table_el[i])
                            print ('Error message:\n'+str(e1))
                            print ('Trying again ('+str(loop_num+1)+' out of '
                                    +str(LOOP_NUM)+')...\n')
                            TIME.sleep(TIME_SLEEP)
                            network1=False
                            loop_num1=loop_num1+1   
                    # check if there is stil no levels of ionization for given element
                    if loop_num1==LOOP_NUM:
                        print ('Unable to obtain levels of ionization for element '
                               +table_el[i]+'\n')
                        TIME.sleep(TIME_SLEEP)
                        # exit program
                        exit_program()
                #--------------------------------------------------------------------------
                #--------------------------------------------------------------------------
        except Exception as e:
            print ('Something went wrong while trying to obtain table of elements '\
                   'that exist in NIST.')
            print ('Error message:\n'+str(e))
            print ('Trying again ('+str(loop_num+1)+' out of '+str(LOOP_NUM)+')...\n')
            TIME.sleep(TIME_SLEEP)
            network=False
            loop_num=loop_num+1
    # check if there is stil no table of elements from NIST
    if loop_num==LOOP_NUM:
        print ('Unable to obtain table of elements that exist in NIST.\n')
        TIME.sleep(TIME_SLEEP)
        # exit program
        exit_program()
    # if everything went well, return data
    return elements,atomic_num_of_el,elements_with_ion,elements_all    

# function for writing elements (with their levels of ionization) to file
def write_el_to_file(filename,list_name,list_el):
    f=open(filename,'a')
    f.write('\n')
    f.write(list_name+'=[')
    if list_name not in ['elements_with_ion','el_as_atom_num_ion_lev_num']:
        for i in range(len(list_el)):
            if i!=(len(list_el)-1):
                f.write('"'+list_el[i]+'", ')
            else:
                f.write('"'+list_el[i]+'"')
    else:
        for i in range(len(list_el)):
            if i!=(len(list_el)-1):
                f.write(str(list_el[i])+', ')
            else:
                f.write(str(list_el[i]))
    f.write(']')
    f.write('\n\n')
    f.close()

# download element table from NIST database
def download_nist_el(nist_element):
    nist_element_plus=nist_element.replace(' ','+')
    print ('Downloading table for element '+nist_element+' from NIST database...\n')
    TIME.sleep(TIME_SLEEP)   
    # flags
    network=False
    loop_num=0
    while (network==False) and (loop_num<LOOP_NUM):
        try:
            with requests.Session() as s:
                # url of element's table for SPECIFIED element
                url=ELEMENTS_TABLE_URL.replace('http://physics.nist.gov/cgi-bin/ASD/'\
                                               'lines1.pl?spectra=','http://physics.'\
                                               'nist.gov/cgi-bin/ASD/lines1.pl?'\
                                               'spectra='+nist_element_plus)
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
                    return nistTable
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
        return nistTable 
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
        # this is sorted by relative intensity, and then by 
        # wavelength (wavelengths were sorted by default)
        nistTable=[[a,b,c] for (a,b,c) in sorted(zip(relativeIntensity,wavelength,reference), 
                   key=lambda pair: pair[0], reverse=True)]
        # if table is empty
        if nistTable==[]:
            print ('Downloaded NIST table for element '+nist_element+' is empty!\n')
            TIME.sleep(TIME_SLEEP)
            return nistTable
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
            return nistTable
    except Exception as e:
        print ('Something went wrong while trying to extract and rearrange '\
               'data from the table.')
        print ('Error message:\n'+str(e)+'\n')
        TIME.sleep(TIME_SLEEP)
        nistTable=[]
        return nistTable

# function that creates table for element in specific format
def create_table(nist_element):
    elTable=download_nist_el(nist_element)
    if elTable!=[]:
        elementName=nist_element.split()[0]
        elementIonization=nist_element.split()[1]
        atomic_num_ion_num=el_all_as_atom_num_ion_lev_num[elements_all.index(nist_element)]
        ri_max_val=max([elTable[i][0] for i in range(len(elTable))])        
        # this is sorted by relative intensity (because I downloaded element table like that)
        elTable=[[atomic_num_ion_num,elementName,elementIonization,elTable[i][1],
                  elTable[i][0],round(((100.0*elTable[i][0])/ri_max_val)/100.0,4),flag,
                  elTable[i][2]] for i in range(len(elTable))]
        # sort now by wavelength and return in format [[atomic_num.ion_num], [name], ...,
        # ..., [reference]]
        elTable=[[elTable[i][k] for i in range(len(elTable))] for k in range(len(elTable[0]))]
        elTable=[[a0,a1,a2,a3,a4,a5,a6,a7] for (a3,a0,a1,a2,a4,a5,a6,a7) in
                 sorted(zip(elTable[3],elTable[0],elTable[1],elTable[2],elTable[4],elTable[5],
                            elTable[6],elTable[7]), key=lambda pair: pair[0], reverse=False)]
        elTable=[[str(elTable[i][k]) for i in range(len(elTable))] 
                 for k in range(len(elTable[0]))]
    return elTable

# write list to file
def write_to_file(filename,listOfData):
    with open(filename, 'w') as f:
        for i in range(len(listOfData)):
            if i>0:
                item_str='\t'.join(listOfData[i])
            else:
                item_str=listOfData[i][0]
            f.write(item_str+'\n')

##############################################################################################
##############################################################################################


##############################################################################################
########################################## PROGRAM ###########################################

print ('########################## Running script on '+currentDateTime+
       ' ##########################\n')

# obtaining table of elements with their levels of ionization
elements,atomic_num_of_el,elements_with_ion,elements_all=retrive_elem_and_ions()
if elements==[] or atomic_num_of_el==[] or elements_with_ion==[] or elements_all==[]:
    print ('Obtained table is empty.')
    print ('Please check.\n')
    TIME.sleep(TIME_SLEEP)
    # exit program
    exit_program()

try:
    # element with the most ionization levels will be max ionization level
    max_ionization=max([roman.fromRoman(e.split()[1]) for e in elements_all])    
    # create list of ionization levels
    ionization_levels=[roman.toRoman(i) for i in range(1,max_ionization+1)]    
    # create list of ionization levels as numbers
    ionization_levels_num=[str(i) if i>9 else '0'+str(i) for i in range(max_ionization)]    
    # all elements represented as atomic number and ionization level num (list of lists)
    el_as_atom_num_ion_lev_num=[[atomic_num_of_el[elements.index(e[i].split()[0])]+'.'
                                 +ionization_levels_num[ionization_levels.index(e[i].split()[1])] 
                                 for i in range(len(e))] for e in elements_with_ion]    
    # all elements represented as atomic number and ionization level num (single list)
    el_all_as_atom_num_ion_lev_num=[item for sublist in el_as_atom_num_ion_lev_num 
                                    for item in sublist]    
    # current working directory
    cwd=os.getcwd()    
    # nist file
    nist_file=os.path.join(cwd,nist_filename)    
    # if file already existed, delete and create new one
    if os.path.isfile(nist_file):
        os.remove(nist_file)    
    # write to nist file
    write_el_to_file(nist_file,'elements',elements)
    write_el_to_file(nist_file,'atomic_num_of_el',atomic_num_of_el)
    write_el_to_file(nist_file,'elements_with_ion',elements_with_ion)
    write_el_to_file(nist_file,'elements_all',elements_all)
    write_el_to_file(nist_file,'el_as_atom_num_ion_lev_num',el_as_atom_num_ion_lev_num)
    write_el_to_file(nist_file,'el_all_as_atom_num_ion_lev_num',
                     el_all_as_atom_num_ion_lev_num)
    print ('File '+nist_filename+' was successfully created.\n')
    TIME.sleep(TIME_SLEEP)    
    # path to folder containing elements
    elements_folder_path=os.path.join(cwd,elements_folder)    
    # if folder already existed, delete folder
    if os.path.isdir(elements_folder_path):
        shutil.rmtree(elements_folder_path)    
    # create elements folder
    os.mkdir(elements_folder_path)
    print ('Folder /'+elements_folder+'/ was successfully created.\n')
    TIME.sleep(TIME_SLEEP)
    print ('Creating relevant folders and files for NIST elements.\n')
    TIME.sleep(TIME_SLEEP)
    # go trough the list of elements ['H', 'He', ...]
    for i in range(len(elements)):
        print ('-------------------------------------------------------------------')
        # create directory for that element
        element_dir=os.path.join(elements_folder_path,elements[i])
        os.mkdir(element_dir)
        print ('Folder /'+elements[i]+'/ was successfully created inside /'
               +elements_folder+'/ folder.\n')
        TIME.sleep(TIME_SLEEP)
        # go trough the list of element's ionization levels e.g. ['He I', 'He II']
        print ('Element '+elements[i]+' has following ionization levels:')
        print (elements_with_ion[i])
        print ('\n')
        TIME.sleep(TIME_SLEEP)
        for j in range(len(elements_with_ion[i])):
            # create table
            elTable=create_table(elements_with_ion[i][j])
            el_fname=elements_with_ion[i][j].replace(' ','_')
            if elTable==[]:
                print ('File '+el_fname+'.dat was not created.\n')
                TIME.sleep(TIME_SLEEP)
            else:
                # rearrange data
                elTable_transpose=list(map(list, zip(*elTable)))
                # header for file
                header=['atomic_num.ion_num\tname\tionization\twavelength(Ang)\t'\
                        'relative_intensity\tfrac_of_max_rel_int\tflags\treference']
                elTable_transpose.insert(0,header)
                # write file
                el_file_path=os.path.join(element_dir,el_fname+'.dat')
                write_to_file(el_file_path,elTable_transpose)
                print ('File '+el_fname+'.dat was successfully created.\n')
                TIME.sleep(TIME_SLEEP)
            print ('\n')
        # check if element folder is empty
        if os.listdir(element_dir)==[]:
            # remove that folder
            print ('\n')
            print ('Removing folder /'+elements[i]+'/ because it is empty.\n')
            TIME.sleep(TIME_SLEEP)
            shutil.rmtree(element_dir)
        print ('-------------------------------------------------------------------\n\n')    
    endTime=datetime.datetime.now()
    executionTime=endTime-startTime
    print ('######################## Total execution time of the script ---> '
           +str(executionTime)+' #########################')
    print ('\n\n')
except Exception as e:
    print ('Something went wrong during script execution.')
    print ('Error message:\n'+str(e))
    print ('Please check.\n')
    TIME.sleep(TIME_SLEEP)
    # exit program
    exit_program()

##############################################################################################
##############################################################################################



