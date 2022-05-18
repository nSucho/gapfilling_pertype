# gapfilling_pertype

The program for my bachelor-thesis providing gapfilling for ENTSOE data.

Needs Python 3.8 for FEDOT

1. readin_main.py
   -> Reads in every month of the year and checks it for gaps for every combination of 'AreaTypeCode', 'technology' and
   'country'
   -> afterwards unifies the all months  to one file
2. gap_filling.py
   -> 
