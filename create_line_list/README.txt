
create_line_list.py is a python script for obtaining atomic lines from the NIST catalog,
based on relating to the specified relative intensity of the lines for each element.

(NIST webpage for retrieving atomic lines by element: http://physics.nist.gov/PhysRefData/ASD/lines_form.html)


To obtain the list of atomic lines for the required elements, follow these steps:


1. Inside folder /create_line_list/ there are the following folders:
   
   * /list_of_elements/       - folder where you put files that contain elements you want to download from the NIST database
   
   * /manually_added_lines/   - folder where you put files that contain manually added lines
   
   * /NIST_ELEMENTS/          - downloaded library of the NIST database

   * /script_results/          - folder with results from the script execution 
   

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


