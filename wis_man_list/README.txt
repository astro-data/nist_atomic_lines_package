

# The script searches for the missing WISeREP lines (obtained from wis_el_and_lines.txt) in the specified files.


# The script has 1 parameter:

  * files - where you put the list of files in which you want to search missing WISeREP lines
                  
            e.g. [file1.txt,file2.txt]
                  
            NOTE: * the files that you specify and which you want to use must be placed 
                  in the folder: /wis_man_list/files_for_search/

		  * This/ese file/s can be the resulting file/s created under
		  /create_line_list/script_results/ 

                  

# The script is called in the following way:
      
  python wis_man_list.py files=[file1.txt,file2.txt]


# The result of the script will be files: [missing_wis_lines_in_file1.txt,missing_wis_lines_in_file2.txt]
  that will be placed in the folder: /wis_man_list/results/

