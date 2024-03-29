
The script creating_nist_lib.py creates library of all lines (with Relative Intensity) that exist in NIST database.

Output of the script are NIST_all_el_and_their_ion.txt file and /NIST_ELEMENTS/ folder.

Library (folder) /NIST_ELEMENTS/ will contain all elements from NIST (as subfolders): 

* /NIST_ELEMENTS/H/ 
* /NIST_ELEMENTS/He/
* /NIST_ELEMENTS/Mg/
* /NIST_ELEMENTS/Ca/
* /NIST_ELEMENTS/Fe/ 
...

and for each element all existing ionization levels (as files):

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

- if running script from weizmann astro-server use @weizmann.ac.il for email account

- if running script from weizmann astro-server use TIME_SLEEP=0.001 (or just 0)

- for CRONTAB: python creating_nist_lib.py > creating_nist_lib_LOG.txt (in order to create creating_nist_lib_LOG.txt (with appending properties...) )

