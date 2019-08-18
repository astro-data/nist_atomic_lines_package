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
import re
from collections import OrderedDict
import time as TIME
import matplotlib.pyplot as plt
from scipy import interpolate
from PARAMETERS import TIME_SLEEP,spectra_files,redshift,legend,line_list_files,\
velocities,spec_shift,space_btw_el_lines,space_btw_files,plt_colormap,\
plot_title_font_size,plot_title_font_weight,size_spec_leg_fonts,\
leg_0_back_col,leg_0_edge_col,leg_0_font_weight,size_el_li_leg_fonts,\
leg_1_back_col,leg_1_edge_col,leg_1_font_weight,dashed_lines_width,\
dashed_lines_style,c,delimeters,header,num_of_tabs,dashed_lines


############################################### FUNCTIONS #####################################################

# read spectrum data
def read_spectrum(spectrum_file,z):
    try:
        print ("Reading data from spectrum file: "+spectrum_file+"...")
        TIME.sleep(TIME_SLEEP)
        # get spectrum data
        f=open(os.path.join(spectra_dir,spectrum_file),'r')
        spectrum_data=f.read().splitlines()
        f.close()
        # rearrange spectrum data
        spectrum_data=[re.split(delimeters,d) for d in spectrum_data]
        spectrum_data=[[d[i] for i in range(len(d)) if d[i]!=''] for d in spectrum_data]
        spectrum_data=[d for d in spectrum_data if d!=[]]
        if not all(len(d)==len(spectrum_data[0]) for d in spectrum_data):
            print ("\nError reading spectrum file: "+spectrum_file)
            print ("Some rows in spectrum have different number of columns.")
            print ("Please check this and correct.\n")
            TIME.sleep(TIME_SLEEP)
            return [],[]
        if spectrum_data==[]:
            print ("Spectrum file is empty!\n")
            TIME.sleep(TIME_SLEEP)
            return [],[]
        # observed wavelength
        wl_observed=[float(e[0]) for e in spectrum_data]
        # rest wavelength
        wl_rest=[wl/(1+z) for wl in wl_observed]
        # flux
        flux=[float(e[1]) for e in spectrum_data]
        # normalized flux
        max_flux=max(flux)
        normalized_flux=[(e/max_flux) for e in flux]
        print ("...OK\n")
        TIME.sleep(TIME_SLEEP)
        # return
        return wl_rest,normalized_flux
    except Exception as e:
        print ("\nSomething went wrong while trying to read spectrum file: "+spectrum_file)
        print ("Error message:\n"+str(e))
        print ("Please check this and correct\n")
        TIME.sleep(TIME_SLEEP)
        return [],[]

# function that takes file (list of lines) and retrieves data from it
def read_el_lines(filename):
    try:
        print ("Reading elements and their lines from file: "+filename+"...")
        TIME.sleep(TIME_SLEEP)
        # file path
        file_path=os.path.join(line_list_dir,filename)
        # open and read file
        f=open(file_path,'r')
        data=f.read().splitlines()
        f.close()
        # take only rows that contain el lines
        data=[e for e in data if e.count('\t')==num_of_tabs]
        data=[e.split('\t') for e in data if e.split('\t')!=header]
        if data==[]:
            print ("File is empty!\n")
            TIME.sleep(TIME_SLEEP)
            return [],[]
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
        print ("...OK\n")
        TIME.sleep(TIME_SLEEP)
        # return data
        return elements_unique,wavelengths
    except Exception as e:
        print ("\nSomething went wrong while trying to read elements and their "\
               "lines from file: "+filename)
        print ("Error message:\n"+str(e))
        print ("Please check this and correct.\n")
        TIME.sleep(TIME_SLEEP)
        return [],[]

# function for plotting spectra
def plot_spectra(SPEC,Z,LEG,EL_LIN,V,DASHED_LINES):
    try:        
        # spectra num
        spec_num=len(SPEC)
        print ("Plotting and analyzing spectra...\n")
        TIME.sleep(TIME_SLEEP)
        remove_ind=[]
        # read spectra
        WL_REST=[]
        NORMALIZED_FLUX=[]    
        MIN_WL=[]
        MAX_WL=[]
        MAX_FLUX=[]        
        for i in range(len(SPEC)):
           wl_rest,normalized_flux=read_spectrum(SPEC[i],Z[i])          
           if wl_rest!=[]:
               normalized_flux=[e+spec_shift*i for e in normalized_flux]
               WL_REST.append(wl_rest)
               NORMALIZED_FLUX.append(normalized_flux)
               MIN_WL.append(min(wl_rest))
               MAX_WL.append(max(wl_rest))
               MAX_FLUX.append(max(normalized_flux))
           else:
               spec_num=spec_num-1
               remove_ind.append(i)
        if WL_REST!=[]:
            min_wl=min(MIN_WL)
            max_wl=max(MAX_WL)
            max_flux=max(MAX_FLUX)
        else:
            print ('No spectra for plotting.\n')
            TIME.sleep(TIME_SLEEP)           
        # continue only if there is spectra
        if WL_REST!=[]:
            SPEC=[SPEC[i] for i in range(len(SPEC)) if i not in remove_ind]
            Z=[Z[i] for i in range(len(Z)) if i not in remove_ind]
            LEG=[LEG[i] for i in range(len(LEG)) if i not in remove_ind]
            # read elements and lines from files
            ELEMENTS_UNIQUE=[]
            WAVELENGTHS=[]
            FLUX=[]
            EL_LIN_NEW=[]        
            lineoffset=max_flux+space_btw_files       
            for i in range(len(EL_LIN)):            
                elements_unique,wavelengths=read_el_lines(EL_LIN[i])            
                if elements_unique!=[]:                           
                    wavelengths=[[l[j]/(1-V[i]/c) for j in range(len(l)) 
                                 if l[j]/(1-V[i]/c)>=min_wl and l[j]/(1-V[i]/c)<=max_wl] 
                                 for l in wavelengths]          
                    # check for [] in wavelengths and remove it
                    empty_el_ind=[]   
                    for j in range(len(elements_unique)):
                        if wavelengths[j]==[]:
                            empty_el_ind.append(j)                
                    if empty_el_ind!=[]:
                        elements_unique=[elements_unique[k] for k in range(len(elements_unique)) 
                                         if k not in empty_el_ind]
                        wavelengths=[wavelengths[k] for k in range(len(wavelengths)) if k not in empty_el_ind]                
                    flux=[[(lineoffset+space_btw_el_lines*j) for k in range(len(wavelengths[j]))] 
                          for j in range(len(wavelengths))]            
                    # check again if there is something left
                    if elements_unique!=[]:
                        ELEMENTS_UNIQUE.append(elements_unique)
                        WAVELENGTHS.append(wavelengths)
                        FLUX.append(flux)
                        EL_LIN_NEW.append(EL_LIN[i])
                        space_btw=flux[-1][0]+space_btw_files
                        lineoffset=space_btw
            if ELEMENTS_UNIQUE==[]:
                print ("No elements and lines for plotting.\n")
                TIME.sleep(TIME_SLEEP)
                dashed=False
            else:
                dashed=True
            # build colormap
            cm=plt.cm.get_cmap(plt_colormap)
            colormap=list(cm.colors)
            all_elements=list(set(sum(ELEMENTS_UNIQUE,[])))
            colors=[colormap[i] for i in range(len(all_elements))]
            CMAP=dict(zip(all_elements,colors))
            # PLOTTING
            fig=plt.figure()
            plt.grid(True)
            plt.xlabel('Rest Wavelength [$\AA$]')
            plt.ylabel('Flux [erg cm$^{-2}$ s$^{-2}$ $\AA$$^{-1}$]')          
            # plotting spectra
            lines_spectra=[]
            F=[]        
            for i in range(len(WL_REST)):
                s,=plt.plot(WL_REST[i],NORMALIZED_FLUX[i])
                lines_spectra.append(s)
                F.append([WL_REST[i],NORMALIZED_FLUX[i]])       
            if spec_num>1:
                title_spectra='SPECTRA'
                title_plot='Spectra analysis of "'+'", "'.join(LEG)+'"'
            else:
                title_spectra='SPECTRUM'
                title_plot='Spectrum analysis of "'+LEG[0]+'"'
            legend_spectra=plt.legend(lines_spectra,LEG,loc='upper right',bbox_to_anchor=(1,1),
                                      bbox_transform=fig.transFigure,title=title_spectra,
                                      prop={'size': size_spec_leg_fonts,'weight':leg_0_font_weight})
            frame_0=legend_spectra.get_frame()
            frame_0.set_facecolor(leg_0_back_col)
            frame_0.set_edgecolor(leg_0_edge_col)
            # plotting elements and lines
            # find file with max num of elements
            if ELEMENTS_UNIQUE!=[]:
                max_num_el=max([len(e) for e in ELEMENTS_UNIQUE])
            else:
                max_num_el=0        
            # go trough every list of elements
            for i in range(len(ELEMENTS_UNIQUE)):
                if len(ELEMENTS_UNIQUE[i])<max_num_el:
                    add_num=max_num_el-len(ELEMENTS_UNIQUE[i])
                    add_list=[[]]*add_num
                    add_el=['']*add_num
                    ELEMENTS_UNIQUE[i]=ELEMENTS_UNIQUE[i]+add_el
                    WAVELENGTHS[i]=WAVELENGTHS[i]+add_list
                    FLUX[i]=FLUX[i]+add_list
            for i in range(len(ELEMENTS_UNIQUE)):
                ELEMENTS_UNIQUE[i].insert(0,EL_LIN_NEW[i])
                WAVELENGTHS[i].insert(0,[])
                FLUX[i].insert(0,[])
            lines=[]           
            EL_AND_LINES=[]
            EL_AND_LINES_VAL=[]            
            for i in range(len(ELEMENTS_UNIQUE)):
                el_color=leg_1_back_col
                l,=plt.plot(WAVELENGTHS[i][0],FLUX[i][0],'v',color=el_color)
                lines_el_lines=[l]
                for j in range(1,len(ELEMENTS_UNIQUE[i])):          
                    if ELEMENTS_UNIQUE[i][j]!='':
                        el_color=CMAP[ELEMENTS_UNIQUE[i][j]]
                    else:
                        el_color=leg_1_back_col
                    l,=plt.plot(WAVELENGTHS[i][j],FLUX[i][j],'v',color=el_color)                   
                    EL_AND_LINES.append([ELEMENTS_UNIQUE[i][j],EL_LIN_NEW[i]])
                    EL_AND_LINES_VAL.append([WAVELENGTHS[i][j],FLUX[i][j],el_color])                    
                    lines_el_lines.append(l)
                lines.append(lines_el_lines)
            EL=sum(ELEMENTS_UNIQUE,[])
            LI=sum(lines,[])
            if ELEMENTS_UNIQUE!=[]:
                legend_elem_lines=plt.legend(LI,EL,loc='upper left',
                                             bbox_to_anchor=(0,1),bbox_transform=fig.transFigure,
                                             prop={'size': size_el_li_leg_fonts,'weight':leg_1_font_weight},
                                             ncol=len(EL_LIN_NEW))   
                frame_1=legend_elem_lines.get_frame()
                frame_1.set_facecolor(leg_1_back_col)
                frame_1.set_edgecolor(leg_1_edge_col)            
            # PLOT DASHED LINES (only if there are spectra, elements and lines)
            if dashed==True:               
                # calculate functions
                FUNCTIONS=[]
                for i in range(len(F)):
                    f=interpolate.interp1d(F[i][0],F[i][1])
                    FUNCTIONS.append(f)
                # go trough dashed list and plott
                for i in range(len(DASHED_LINES)):
                    # take file
                    e_filename=DASHED_LINES[i][1]
                    # take element
                    e_name=DASHED_LINES[i][0]
                    # take spectrum
                    e_spectrum=DASHED_LINES[i][2]
                    print ("Plotting element '"+e_name+"' from file '"+e_filename+"' on spectrum '"+
                           e_spectrum+"'...")
                    TIME.sleep(TIME_SLEEP)
                    # check if spectrum, element and file exists
                    if (e_spectrum in LEG) and ([e_name,e_filename] in EL_AND_LINES):
                        # legend index
                        leg_ind=LEG.index(e_spectrum)
                        # function for given spectrum
                        func=FUNCTIONS[leg_ind]
                        # WL-s of element
                        e_WL=EL_AND_LINES_VAL[EL_AND_LINES.index([e_name,e_filename])][0]
                        # FLUX of element
                        e_FLUX=EL_AND_LINES_VAL[EL_AND_LINES.index([e_name,e_filename])][1]
                        # COLOR of element
                        e_COLOR=EL_AND_LINES_VAL[EL_AND_LINES.index([e_name,e_filename])][2]
                        # plot dashed lines
                        for k in range(len(e_WL)):
                            if (e_WL[k]>=min(F[leg_ind][0])) and (e_WL[k]<=max(F[leg_ind][0])):
                                plt.vlines(x=e_WL[k],ymin=func(e_WL[k]),ymax=e_FLUX[k],
                                           linewidth=dashed_lines_width,color=e_COLOR,
                                           linestyle=dashed_lines_style)
                        print("...OK\n")
                        TIME.sleep(TIME_SLEEP)
                    else:
                        if e_spectrum not in LEG:
                            print ("\nSpecified spectrum '"+e_spectrum+"' is not on the graph - "+title_plot)
                            print ("Please provide correct spectrum name.\n")
                            TIME.sleep(TIME_SLEEP)
                        if [e_name,e_filename] not in EL_AND_LINES:
                                print ("\nSpecified ['"+e_name+"', '"+e_filename+"'] is not on the graph - "+
                                       title_plot)
                                print ("Please provide existing combination of element name and file name.\n")
                                TIME.sleep(TIME_SLEEP)          
            # SHOW PLOT
            axes=plt.gca()
            # add legends
            axes.add_artist(legend_spectra)
            if ELEMENTS_UNIQUE!=[]:
                axes.add_artist(legend_elem_lines)    
            figManager = plt.get_current_fig_manager()
            figManager.window.showMaximized()    
            plt.title(title_plot,fontsize=plot_title_font_size,
                      fontweight=plot_title_font_weight)
            plt.show()
    except Exception as e:     
        print ("Something went wrong while trying to plot and analyze spectra.")
        print ("Error message:\n"+str(e))
        print ("Please check this and correct.\n")
        TIME.sleep(TIME_SLEEP)

###############################################################################################################


############################################## PROGRAM ########################################################

# FOLDERS
# current working directory
cwd=os.getcwd()
# spectra directory
spectra_dir=os.path.join(cwd,'spectra_files')
# line lists directory
line_list_dir=os.path.join(cwd,'line_list_files')

# go trough every spectra file
for i in range(len(spectra_files)):
    # plot and analyze spectra
    print ("------------------------------------------------------------\n")
    plot_spectra(
                 spectra_files[i],
                 redshift[i],
                 legend[i],
                 line_list_files[i],
                 velocities[i],
                 dashed_lines[i]
                )
    print ("------------------------------------------------------------\n\n\n")

###############################################################################################################




