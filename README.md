# NIST ATOMIC LINES PACKAGE

The NIST atomic lines package serves for obtaining atomic lines (which contain Relative Intensity information) from the NIST catalog and analyzing spectra using those lines.

The package contains the following folders:
- /nist_library/
- /create_line_list/
- /search_lines/
- /wis_man_list/
- /analyze_spec/


# /nist_library/

This folder contains python script creating_nist_lib.py that creates a library of all lines (with Relative Intensity) that exist in NIST database.

Library (folder) /NIST_ELEMENTS/ will contain all elements form NIST (as subfolders): 

* /NIST_ELEMENTS/H/ 
* /NIST_ELEMENTS/He/
* /NIST_ELEMENTS/Mg/
* /NIST_ELEMENTS/Ca/
* /NIST_ELEMENTS/Fe/ 
...

and for each element all existing ionization levels (in separate files):

* /NIST_ELEMENTS/H/
  - H_I.dat

* /NIST_ELEMENTS/C/
  - C_I.dat
  - C_II.dat
  - C_III.dat
  - C_IV.dat
  - C_V.dat
...


NOTE:

- If running script from weizmann astro-server use @weizmann.ac.il for email account and TIME_SLEEP=0.001 (or just 0)

- For CRONTAB: python creating_nist_lib.py > creating_nist_lib_LOG.txt (in order to create creating_nist_lib_LOG.txt (with appending properties...) )


# /create_line_list/

This folder contains python script create_line_list.py for obtaining atomic lines from the NIST catalog,
based on relating to the specified relative intensity of the lines for each element.

(NIST webpage for retrieving atomic lines by element: http://physics.nist.gov/PhysRefData/ASD/lines_form.html)


To obtain the list of atomic lines for the required elements, follow these steps:


1. Inside folder /create_line_list/ there are the following folders:
   
   * /list_of_elements/       - folder where you put files that contain elements you want to download from the NIST database
   
   * /manually_added_lines/   - folder where you put files that contain manually added lines
   
   * /NIST_ELEMENTS/          - downloaded library of the NIST database

   * /script_result/          - folder with results from the script execution 
   

2. File that you put in /list_of_elements/ folder should contain required elements (with ionization levels)

   For example file list_of_lines_example.txt should be like:

   H I
   
   He I [0,0.2,0,2000,10000]
   
   He II
   
   O I
   
   O II [50,0.3,0,3000,15000]
   
   ...
   

   NOTE : You cannot put element without specifying ionization level.


3. For each element it is possible to specify the required parameter combination:

   [% of data, fraction of max rel int, min rel int, lower wavelength, upper wavelength]

   - WLs are in Ang.
   - If e.g. we specify [50,0.2,...] and more lines are retrieved according to the criterion of
     50%, then this will be the governing parameter.

   If nothing is specified for an element, the default parameter combination is: [50,0.2,0,2000,10000]
   (or something else if it is changed inside a script)

   If wanting to ignore a given parameter, zero should be specified  (like in the default combination above, for min rel int).

   If wanting to retrieve everything within some range then use [0,0,0,3000,15000]

   If wanting to retrieve everything that exist for specifed element then use [0,0,0,0,0]


4. File that you put in /manually_added_lines/ folder should contain additional specific lines 
   which will be united with the lines retrieved from the NIST website to a single output file.
 
   When adding lines, note the following:

   - Elements of line (atomic_num.ion_num, name, ionization,..) need to be TAB separeted
   - If there is an element of line that has more than one value (flags or reference element can have multiple values)
     then between each value shoud be ; and NO SPACE (example for flags P;M;T)
   - Flags: P=Persistent, M=Manually added, F=Forbidden, T=Telluric, G=Galaxy (host) lines, S=Sky lines (atmosphere)
   - If there is no value for relative_intensity (frac_of_max_rel_int) in line, then you NEED to put null (null) value
   - If there is no value for flags or reference, leave EMPTY
   - NOTE: You can add TEXT FREE comments, empty new lines, etc..
   - If something is not clear, use manually_added_lines_example.txt as an example


5. When everything is prepared, execution of the script can be performed in the following ways:
   
   python create_line_list.py [optional agruments] 
   
   Arguments are:
   
   - ELEMENTS_FILE=some_filename_1.txt
   
   - MAN_LINES_FILE=some_filename_2.txt

   - library=[True,False] (if not specified library=True)
     (if library=True --> script will work "offline" and search /NIST_ELEMENTS/ for retrieving atomic lines by element)
     (if library=False --> script will work "online" and search NIST webpage for retrieving atomic lines by element)
   
   - output=[all, list, matlab] (if not specified output=all)
     (if output=list --> output will be file listing all the retrieved lines : list_of_lines_[datetime].txt)
     (if output=matlab --> output will be MATLAB file listing all the retrieved lines : MATLAB_file_[datetime].txt)
     (if output=all --> output will be both files)

   - rel_int_flag=[all, range] (if not specified rel_int_flag=all)
     (rel_int_flag=all ---> For maximum rel. intensity of the element, the maximum rel. intensity for all element lines was taken.)
     (rel_int_flag=range ---> For maximum rel. intensity of the element, the maximum rel. intensity for specified range of element 
                              lines was taken.)  
     This means that % of data and fraction of max rel int parameters will depend on rel_int_flag (because they depend on max rel int).
     
     NOTE: all created files will be under folder: /create_line_list/script_result/ 
   
   e.g.

   python create_line_list.py ELEMENTS_FILE=elements.txt MAN_LINES_FILE=added_lines.txt output=list rel_int_flag=range
   
   python create_line_list.py ELEMENTS_FILE=elements.txt library=True output=matlab
   
   python create_line_list.py MAN_LINES_FILE=added_lines.txt rel_int_flag=range
   
   python create_line_list.py ELEMENTS_FILE=elements.txt output=list rel_int_flag=all
   
   ...
   

# /search_lines/

- This folder contains python script search_lines.py that searches for the specified lines (wavelengths in Ang) in the specified files

- The script has 2 parameters:

  * files - where you put the list of NIST files in which you want to search for lines
                  
            e.g. [file1.txt,file2.txt]
                  
            NOTE: the files that you specify and which you want to use must be placed 
                  in the folder: /search_lines/files_for_search/

  * lines - where you put the list of lines you are looking for
                 
            e.g. [[4500,50],[7000,20]]
                  
            This means looking for a lines:
            - 4500 Ang in a range +/- 50 Ang (range 4450 - 4550 Ang) in [file1.txt,file2.txt]
            - 7000 Ang in a range +/- 20 Ang (range 6980 - 7020 Ang) in [file1.txt,file2.txt]

- The script is called in the following way:
      
  e.g. python search_lines.py files=[file1.txt,file2.txt] lines=[[4200,40],[5750,25]]

- The result of the script is the file: search_lines_CURRENT_DATE_TIME.txt that will be placed in the folder: /search_lines/results/


# /wis_man_list/

- This folder contains python script wis_man_list.py that searches for the missing WISeREP lines (obtained from wis_el_and_lines.txt) in the specified files.

- The script has 1 parameter:

  * files - where you put the list of files in which you want to search missing WISeREP lines
                  
            e.g. [file1.txt,file2.txt]
                  
            NOTE: * the files that you specify and which you want to use must be placed 
                  in the folder: /wis_man_list/files_for_search/

		  * This/ese file/s can be the resulting file/s created under
		  /create_line_list/script_results/ 

- The script is called in the following way:

  python wis_man_list.py files=[file1.txt,file2.txt]

- The result of the script will be files: [missing_wis_lines_in_file1.txt,missing_wis_lines_in_file2.txt]
  that will be placed in the folder: /wis_man_list/results/


# /analyze_spec/

- This folder contains python script analyze_spec.py that analyze spectra for given lists of elements with their lines.

- Spectra files must be placed under /analyze_spec/spectra_files/ folder.

- Elements (with their lines) that we want to use are in the files that we place under /analyze_spec/line_list_files/ folder.

- Elements (with their lines) must be in specific format inside the files (see "header" of line list files in PARAMETERS.py)

- We can analyze one or more spectra on the same plot and we can have multiple plots.

- We can use one or more files (that contain elements with their lines) for analyzing the spectrum/spectra (of same plot).

- We can plot dashed lines for specified elements and their lines.

- Everything should be carefuly specified in the PARAMETERS.py file before using analyze_spec.py script.


