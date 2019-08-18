

# The script searches for the specified lines (wavelengths in Ang) 
  in the specified files


# The script has 2 parameters:

  * files - where you put the list of NIST files in which you want to search for lines
                  
            e.g. [file1.txt,file2.txt]
                  
            NOTE: the files that you specify and which you want to use must be placed 
                  in the folder: /search_lines/files_for_search/

  * lines - where you put the list of lines you are looking for
                 
            e.g. [[4500,50],[7000,20]]
                  
            This means looking for a lines:
            - 4500 Ang in a range +/- 50 Ang (range 4450 - 4550 Ang) in [file1.txt,file2.txt]
            - 7000 Ang in a range +/- 20 Ang (range 6980 - 7020 Ang) in [file1.txt,file2.txt]
                  

# The script is called in the following way:
      
  e.g. python search_lines.py files=[file1.txt,file2.txt] lines=[[4200,40],[5750,25]]


# The result of the script is the file: search_lines_CURRENT_DATE_TIME.txt
  that will be placed in the folder: /search_lines/results/


