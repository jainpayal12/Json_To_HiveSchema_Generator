# Json_To_HiveSchema_Generator
Json_To_HiveSchema_Generator is a tool designed to automatically generate hive schema from JSON. This takes json input_file path and schemaName(optional) as command line argument. The output, can then be used to create hive table.

#### NOTE : 
The tool can read JSON-formatted data only if it is in a particular format. Each row in the file has to be a JSON dictionary where the keys specify the column names and the values specify the table content.

## Pre-Requisites

    Python 2.7
    Ubuntu 14.04 or greater 

## Execution

    git clone https://github.com/jainpayal12/Json_To_HiveSchema_Generator.git

##  Install the pre_requisites
##  Assuming you have Ubuntu System

    $ cd <cloned_repository>/run
    $ sh install.sh

## Run the python file
    $ cd <cloned_repository>/lib
    $ python schemaGenerator.py </absolutepath/of/json/inputFile> <schemaName>(optional)
    
