# latexqol

Under construction. Currently only 1 function.

## Example use

To copy a simple Latex formated table from a list of data arrays to you clipboard
'''Python
from latexqol import copy_table

headers = ["header1", "header2", "header3"]
col1 = [1, 2, 3]
col2 = [4, 5, 6]
col3 = [7, 8, 9]

copy_table(headers, col1, col2, col3)
'''
