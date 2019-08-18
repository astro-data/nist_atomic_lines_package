#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Developed and tested on:

- Linux 18.04 LTS
- Windows 10
- Python 3.7 (Spyder)

@author: Nikola Knezevic
"""


################################## PARAMETERS ##################################

# spectra files that we want to analyze (EXAMPLE)
spectra_files_1=['SN2018cmt_2018_06_18.txt']
spectra_files_2=['SN2018cnv_2018_06_18.txt']
spectra_files_3=['SN2016hnk_2016_10_31.flm','SN2016hnk_2016_11_02.asci']
spectra_files=[spectra_files_1,spectra_files_2,spectra_files_3]      

# redshift (if value is not known or not specified, default should be 0)
# each redshift must corespond to each spectrum file
redshift_1=[0.047]
redshift_2=[0.074]
redshift_3=[0.016,0.016]
redshift=[redshift_1,redshift_2,redshift_3]

# legend (if value is not known or not specified, default should be 
#         'spectrum_1','spectrum_2',...,'spectrum_N')
# each legend must corespond to each spectrum file
legend_1=['SN2018cmt 2018-06-18']       
legend_2=['SN2018cnv 2018-06-18']        
legend_3=['SN2016hnk 2016-10-31','SN2016hnk 2016-11-02']
legend=[legend_1,legend_2,legend_3]      

# line list files 
# for each spectrum (or spectra) there is a list of line files that we want to use
line_list_files_1=['lines_1.txt', 'lines_2.txt']
line_list_files_2=['lines_2.txt', 'lines_3.txt']
line_list_files_3=['lines_1.txt']
line_list_files=[line_list_files_1,line_list_files_2,line_list_files_3]

# velocities (if value is not known or not specified, default should be 0)
# each velocity must corespond to each line file
velocities_1=[0,0]
velocities_2=[0,0]
velocities_3=[0]
velocities=[velocities_1,velocities_2,velocities_3]

# create dashed list of lines 
# (if value is not known or not specified default should be dashed_lines_N = [])
# each value in the dashed list of lines should be in te following format:
# ['element name', 'file where element lines are', 'spectrum legend name']
# each dashed line list must corespond to each spectrum file
dashed_lines_1=[
                ['Na II','lines_1.txt','SN2018cmt 2018-06-18'],
                ['C II','lines_2.txt','SN2018cmt 2018-06-18'],
                ['Fe III','lines_1.txt','SN2018cmt 2018-06-18']
               ]
dashed_lines_2=[
                ['He II','lines_3.txt','SN2018cnv 2018-06-18'],
                ['Fe III','lines_3.txt','SN2018cnv 2018-06-18']
               ]
dashed_lines_3=[
                ['N I','lines_1.txt','SN2016hnk 2016-10-31'],
                ['Na II','lines_1.txt','SN2016hnk 2016-10-31'],
                ['Fe III','lines_1.txt','SN2016hnk 2016-11-02']
               ]
dashed_lines=[dashed_lines_1,dashed_lines_2,dashed_lines_3]


# sleeping time (in sec)
TIME_SLEEP=0

# spectrum shift (if not specified default is spec_shift=0)
spec_shift=0.5

# space btw diff elements in same set of lines
space_btw_el_lines=0.04

# space btw diff set of lines
space_btw_files=0.4

# color map for matplotlib
plt_colormap='tab20b'

# plot title
plot_title_font_size=12
plot_title_font_weight='bold'

# spectra legend 
size_spec_leg_fonts=7
leg_0_back_col='white'
leg_0_edge_col='grey'
leg_0_font_weight='bold'

# elements legend
size_el_li_leg_fonts=6
leg_1_back_col='white'
leg_1_edge_col='grey'
leg_1_font_weight='bold'

# dashed lines
dashed_lines_width=1
dashed_lines_style=':'

# lightspeed (km/s)
c=3e5

# delimeters (for spectrum files)
delimeters='\s+|\t+'

# header of a line list files
header=['atomic_num.ion_num','name','ionization','wavelength(Ang)',
        'relative_intensity','frac_of_max_rel_int','flags',
        'reference']

# number of tabs
num_of_tabs=len(header)-1

################################################################################


