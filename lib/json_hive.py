import json
import sys
import os
from deepdiff import DeepDiff


class schemaGenerator:
    """GLOBAL VARIABLES"""
    JSON_Data = [] 

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
 #               sys.stdout.write(self.pretty_print(self.JSON_Data)+'\n')								       #Print JSON content
        except IOError:
            sys.stdout.write("FILE DOES NOT EXIST, PLEASE CHECK THE JSON INPUT FILE PATH\n")  
            sys.exit(0)   

        except ValueError, Argument:
            sys.stdout.write(str(Argument))
	    sys.stdout.write("\n")
            sys.stdout.write("JSON FORMAT ERROR\n")
            sys.exit(0)


    
    def parseDictionary(self,data):
        try:
            print "in find"
            print data

            for k, v in data.items():
                col_name = k
                print col_name
      
                col_type = yield(type(v))
                print col_type

                if isinstance(col_type,dict):
                    for result in find(data[col_name]):
                        print result 
        
                elif isinstance(col_type, list):
                    for result in find(data[col_name]):
                        print result

            
                print col_name,col_type
        except:
               print "error"
            
    #    return



    def parseJSON(self):		                 												               # Parse Json file to create the schema definition 
        schema = ""
        print "in parseJson()"
        for i in range(0,len(self.JSON_Data)):
            print "****************************************************************************************"
            print self.JSON_Data[i]
            print "****************************************************************************************"
            print "Call to parseDict"
            data = self.JSON_Data[i]
            print type(data)
            self.parseDictionary(data)
   


if __name__ == "__main__":
    
        """ Execute $ python schemaGenerator.py <AbsoluteFilePath> <schemaName>
        For instance,  $ python schemaGenerator.py /home/username/Documents/dataset/users.json  userSchema"""
        SG = schemaGenerator()                                                  							 #Class object
        filePath = SG.getInputFilePath()                                     							 #Get the input filepath specified as command line argument
        SG.getJSON_Data(filePath)
#        sys.stdout.write("CREATING HIVE SCHEMA DEFINITION FOR FILE %s WITH SCHEMA_NAME %s\n"%(os.path.basename(filePath),SG.schemaName))
        SG.parseJSON()        

