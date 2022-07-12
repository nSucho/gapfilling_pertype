# gapfilling_pertype

The program for my bachelor-thesis providing gapfilling for ENTSOE data.

Needs Python 3.8 for FEDOT!

1. readin_main.py
   -> Reads in every month of the year and checks it for gaps for every combination of 'AreaTypeCode', 'technology' and
   'country'
   -> afterwards unifies the all months to one file
2. gap_filling.py
   -> reads in the yearly-file with the specified values and creates gaps in that file
   -> fills gaps with the different methods
   -> plots everything

## Where to place the downloaded data
The original-data from the website needs to be under 'data/*TheTypeOfData*/original_data/*year*/'. So for example 
if the data type is '2021_01_AggregatedGenerationPerType_16.1.B_C' and from '2021' the path would be 
'data/agpt/original_data/2021/' and at this location all the csv-files of this year have to be.
The code will save the data then under 'data/agpt/2021/*'.

## How to use the readin_main.py
First choose a year and afterwards the type of data (agpt or totalload). 

## How to use the gap_filling.py
First set the variables. The type of data is again 'agpt' or 'totalload'. Afterwards
choose if you want to create random gaps or if you want to duplicate the gaps from a different file. If the latter you 
also have to specify the country code of the country you want it to duplicate from and also add the atc of the country.
