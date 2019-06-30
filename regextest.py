import re
import os
import json

file = '/Users/seanchan/orbital/testreceipt_formatted.txt'

def parse_into_lines(filename,threshold):

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

                #sort message and find vert_coord at most 5 pixels closest to line, if
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

        print(json.dumps(message,sort_keys=True,indent=4))
        return message
        
        #Keep threshold for text on the same line within 5 pixels
        #Link up lines at the same y-coord from different regions
        
            
    else:
        print('File does not exist!')
    

def main():
    message = parse_into_lines(file,15)
    

if __name__ == '__main__':
    main()
        
    
    
