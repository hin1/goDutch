import re
import os
import json
import pprint
from google.protobuf.json_format import MessageToJson

file = '/Users/seanchan/goDutch/test/testpic3-full_response.txt'

'''MICROSOFT AZURE'''

#Parse a text file in JSON format into a dictionary of keys as vertical coordinate of lines
#and values as a list of the strings identified
def parseToList(filename,threshold):

    if (os.path.exists(filename)):
        with open(filename) as f:
            receipt = json.load(f)
        
        message = {} #Each line is a key y-coord and value of list of words
        regions = receipt["regions"]

        for a in range(len(regions)): 
            lines = regions[a]["lines"]
            
            for b in range(len(lines)): #for each region
                words = lines[b]["words"]
                message_lines = []
                
                for c in range(len(words)): #for each line
                    message_lines.append(words[c]["text"])
                
                vert_coord = int((lines[b]["boundingBox"].split(','))[1]) #second number

                #sort message and find vert_coord at most threshold pixels closest to line, if
                #not then create new key

                same_line = False
                for d in message:
                    if (abs(d-vert_coord) <= threshold):
                        for word in message_lines:
                            message[d].append(word)
                        same_line = True
                        break
                    
                if not same_line:
                    message[vert_coord] = message_lines

        return message
            
    else:
        print('File does not exist!')

#Parse a text file in JSON format into a dictionary of keys as vertical coordinate of lines
#and values as a combined string of the line
def parseToString(filename,threshold):

    if (os.path.exists(filename)):
        with open(filename) as f:
            receipt = json.load(f)
        
        message = {} #Each line is a key y-coord and value of list of words
        regions = receipt["regions"]

        for a in range(len(regions)): 
            lines = regions[a]["lines"]
            
            for b in range(len(lines)): #for each region
                words = lines[b]["words"]
                message_lines = ""
                
                for c in range(len(words)): #for each line
                    message_lines += (words[c]["text"])
                    message_lines += " "
                
                vert_coord = int((lines[b]["boundingBox"].split(','))[1]) #second number

                #sort message and find vert_coord at most threshold pixels closest to line, if
                #not then create new key

                same_line = False
                for d in message:
                    if (abs(d-vert_coord) <= threshold):
                        message[d] += message_lines
                        same_line = True
                        break
                    
                if not same_line:
                    message[vert_coord] = message_lines

        return message
    
    else:
        print('File does not exist!')

#Parse a text file in JSON format into a list of lines as strings
def getStringList(filename,threshold):
    info = parseToString(file,15)
    message = []
    for line in info:
        message.append(info[line])
    print(json.dumps(message,indent=4))
    return message

def main():

    message = google_get_lines(file,10)
    pp = pprint.PrettyPrinter()
    pp.pprint(message)

if __name__ == '__main__':
    main()
          
    
