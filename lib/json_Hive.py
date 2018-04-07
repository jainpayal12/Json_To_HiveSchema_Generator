



import json
import sys
import os
from deepdiff import DeepDiff
import re

class schemaGenerator:
    """GLOBAL VARIABLES"""
    JSON_Data = [] 
    schemaDict = {}

    def getInputFilePath(self):
        argLen = len(sys.argv)

        if argLen >= 2 :     
            inputFilePath = sys.argv[1]
            if argLen > 2:                                    														 # Both filepath and schemaName specified
                self.schemaName = sys.argv[2]
	    else:
                if inputFilePath.startswith('/'):
                    self.schemaName, ext = os.path.splitext(os.path.basename(inputFilePath))
                    sys.stdout.write("SCHEMA NAME ARGUMENT MISSING. USING SCHEMA NAME TO BE THE FILENAME PROVIDED AS INPUT\nI:e %s\n" % self.schemaName)
                else:
                    raise Exception("NOABSOLUTEPATHPROVIDED, PLEASE PROVIDE THE ABSOLUTE FILEPATH OF INPUT JSON FILE")
            return inputFilePath  														                        # Returns absolute filePath
 
        elif argLen < 2:  
            raise IndexError("PLEASE PROVIDE THE JSON INPUT FILE PATH")            
            

    def getJSON_Data(self,filePath):														        #Get content of JSON file
        try:
            with open(filePath) as data_file:     														#Open file
                for line in data_file:
                    self.JSON_Data.append(json.loads(line))
                sys.stdout.write(self.pretty_print(self.JSON_Data)+'\n')								       #Print JSON content
        except IOError:
            sys.stdout.write("FILE DOES NOT EXIST, PLEASE CHECK THE JSON INPUT FILE PATH\n")  
            sys.exit(0)   
        except ValueError, Argument:
            sys.stdout.write(str(Argument))
	    sys.stdout.write("\n")
            sys.stdout.write("JSON FORMAT ERROR\n")
            sys.exit(0)


    def pretty_print(self,js):																	#try to convert json to pretty-print format 
        try:
            return json.dumps(js, indent=4, separators=(",", ":"), sort_keys=True)
        except Exception as e:
            return "%s" % js


    def jsonType_hivesSchemaType(self, var):													#Converts json datatype to hive datatype
    
        if isinstance(var,bool):
            return 'BOOLEAN'  
        if isinstance(var,int):
            if var in range((-(2 ** 8)), ((2 ** 8) - 1)):
                return 'TINYINT'
            elif var in range((-(2 ** 16)), ((2 ** 16) - 1)):
                return 'SMALLINT'
            elif var in range((-(2 ** 32)), ((2 ** 32) - 1)):
                return 'INT'
            elif var in range((-(2 ** 64)), ((2 ** 64) - 1)):
                return 'BIGINT'
    
        elif isinstance(var,float):
            return 'DOUBLE'

        elif isinstance(var,long):
            return 'BIGINT'
        elif isinstance(var,str):
            return 'STRING'
        elif isinstance(var,unicode):
            return 'STRING'
        elif isinstance(var,list):
            return 'ARRAY'
        elif isinstance(var,dict):
            return 'STRUCT'
        else:
            return 'NULL'


    def parseJSON(self):		                 												               # Parse Json file to create the schema definition 
        schema = ""
        self.parseListOfDict(self.JSON_Data)
        for col_name,col_type in self.schemaDict.items():
            schema = schema + col_name + " " + col_type + ",\n\t" 
        schema = schema.strip(',')
        self.createSchemaDefinition(schema) 

           
    def createSchemaDefinition(self,schema):													      # Creates schema definition
        schemaDefn = "create table %s(%s)\n"%(self.schemaName,schema)
        sys.stdout.write("************SCHEMA DEFINITION*********************\n")
        sys.stdout.write(schemaDefn)


    def parseListOfDict(self,data):																# Parses List Of Dictionaries
        tmpDict = {}
        tmp = self.parseDict(data[0])
        self.schemaDict = tmp
        for i in range(1,len(data)):
            tmpDict = self.parseDict(data[i])	
            diff = DeepDiff(self.schemaDict,tmpDict)
            if len(dict(diff)) != 0:
                self.compareElements(self.schemaDict,tmpDict, diff)


    def compareElements(self,d1,d2,difference):
        differenceKeys = []
        differenceKeys = difference.keys()
        for k in differenceKeys:
            if k == 'dictionary_item_added' : 
                 item_add = difference.get('dictionary_item_added')
                 col_name =  (re.search( r'..\D....\D....(\w+).*', str(item_add), re.M|re.I)).group(1)

                 col_type = d2[col_name]
                 for i in range(0,len(item_add)):
                     self.schemaDict.update({str(col_name) : col_type})
                     
            if k == 'values_changed':
                 changedValues= difference.get('values_changed')       
                 for k, v in changedValues.items():
                     col_name = (re.search( r'.\D....(\w+).*', str(k), re.M|re.I)).group(1)
                     value =  v
                     if (len(v['new_value']) < len(v['old_value'])  or  'NULL' in v['new_value']):
                         self.schemaDict.update({str(col_name) : v['old_value']})
                     elif (len(v['new_value']) > len(v['old_value']) or 'NULL' in v['old_value']):
                         self.schemaDict.update({str(col_name) : v['new_value']}) 
    

    def parseDict(self,data):																        # Parse Dictionary
        tmpSchemaDict = {}
        for key,value in data.items():
            col_name = key
            row_data = value
            col_type = ""
            tmpSchemaDict.update({str(col_name) : col_type}) 
            col_type = self.jsonType_hivesSchemaType(row_data)

            if  col_type == "ARRAY":
                nestedType = self.parseList(row_data)
                if nestedType == "NULL" :
                    col_type = "NULL"
                else:      
                    col_type = "ARRAY<%s>"%nestedType

            elif col_type == "STRUCT":
                Dict = self.parseNestedDict(row_data)
                for i,j in Dict.items():  
                    strn = strn + i + ":" + j + ","
                strn = strn.strip(',')
                col_type = "STRUCT<%s>"%strn


            if tmpSchemaDict[key] !=  "NULL" :
                tmpSchemaDict.update({str(col_name) : col_type}) 
        return tmpSchemaDict


     
    def parseList(self,data):																	 #Parse List within dictionary
        strn = ""
        listLen = len(data)
        if listLen > 0 :
            if isinstance(data[0],(int,float,long,str,unicode)):
                Type = self.jsonType_hivesSchemaType(data[0])
                
            elif isinstance(data[0],dict):
                for i in range(0,len(data)):
                    Dict = self.parseNestedDict(data[i])
                    
                for i,j in Dict.items():  
                    strn = strn + i + ":" + j + ","
                strn = strn.strip(',')
                Type = "STRUCT<%s>"%strn

        else:
                Type = "NULL"
             
        return Type 


    def parseNestedDict(self,data):																			#Parse dictionary within dictionary
        nestedDict = {}
        strn = ""
        for key,value in data.items():
            col_name = key
            row_data = value
            col_type = ""
            nestedDict.update({str(col_name) : col_type}) 
            col_type = self.jsonType_hivesSchemaType(value)

            if  col_type == "ARRAY":
                nestedType = self.parseList(row_data)
                if nestedType == "NULL" :
                    col_type = "NULL"
                else:      
                    col_type = "ARRAY<%s>"%nestedType

            elif col_type == "STRUCT":
                nestedType = self.parseNestedDict(row_data)
                for i,j in nestedType.items():  
                    strn = strn + i + ":" + j + ","
                strn = strn.strip(',')
                col_type = "STRUCT<%s>"%strn



            if nestedDict[key] != "NULL" :            
                nestedDict.update({str(col_name) : col_type})  
        return nestedDict

            

if __name__ == "__main__":
    
        """ Execute $ python schemaGenerator.py <AbsoluteFilePath> <schemaName>
        For instance,  $ python schemaGenerator.py /home/username/Documents/dataset/users.json  userSchema"""
        SG = schemaGenerator()                                                  							 #Class object
        filePath = SG.getInputFilePath()                                     							 #Get the input filepath specified as command line argument
        SG.getJSON_Data(filePath)
        sys.stdout.write("CREATING HIVE SCHEMA DEFINITION FOR FILE %s WITH SCHEMA_NAME %s\n"%(os.path.basename(filePath),SG.schemaName))
        SG.parseJSON()        

