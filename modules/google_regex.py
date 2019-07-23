import re
import os
import json
import pprint
from google.protobuf.json_format import MessageToJson
import ast

file = '/Users/seanchan/goDutch/test/testpic3-full_response.txt' #MACS
#file = '/Users/seanchan/goDutch/test/testpic4-text_annotation.txt' #BURGER KING

#For full response
def fget_vert_coord_to_lines(filename,threshold):
    if (os.path.exists(filename)):
        with open(filename) as f:
             response = f.read()

        response = ast.literal_eval(response)

        #Check file type and extract relevant information
        filetype = filename.split('-')[-1]
        if (filetype == "text_annotation.txt"):
            receipt = response[1:] #Take away the first element, which is the entire string
        elif (filetype == "full_response.txt"):
            receipt = response["text_annotations"]
            receipt = receipt[1:] #Take away the first element, which is the entire string

        message = {} #Each line is a key y-coord and value of list of words
        # bounding_poly order is: top left, top right, bottom right, bottom left    
        for word in receipt:
            
            vertices = word["bounding_poly"]["vertices"]
            avg_word_coord = (int(vertices[3]["y"]) + int(vertices[0]["y"]))/2

            is_new_line = True
            #Loop through keys in message which are the vertical coordinates of each line
            for line_coord in message:
                if (abs(line_coord - avg_word_coord) < threshold):
                    message[line_coord] += " "
                    message[line_coord] += word["description"]
                    is_new_line = False
                    break

            if (is_new_line):
                message[avg_word_coord] = word["description"]

        return message
            
    else:
        print("File does not exist.")

def get_vert_coord_to_lines(response,threshold):
    
    receipt = response[1:] #Take away the first element, which is the entire string

    message = {} #Each line is a key y-coord and value of list of words

    # bounding_poly order is: top left, top right, bottom right, bottom left
    
    for word in receipt:
        vertices = word["bounding_poly"]["vertices"]
        avg_word_coord = (int(vertices[3]["y"]) + int(vertices[0]["y"]))/2

        is_new_line = True
        #Loop through keys in message which are the vertical coordinates
        for line_coord in message:
            if (abs(line_coord - avg_word_coord) < threshold):
                message[line_coord] += " "
                message[line_coord] += word["description"]
                is_new_line = False
                break

        if (is_new_line):
            message[avg_word_coord] = word["description"]

    return message


def get_lines(response,threshold):

    message = fget_vert_coord_to_lines(response,threshold)
    #message = get_vert_coord_to_lines(response,threshold)
    lines = []
    for vert_coord in message:
        lines.append(message[vert_coord])

    return lines

'''
Data Structure (List of Dictionaries):
[
    {'item':'item1','price':'price1'},
    {'item':'item2','price':'price2'},
    ....
]
'''
def get_item_price_dict(receipt):

    data = []
    
    '''
    #Possible formats (Optional, may not even have format line)
    # quantity: 'quantity','QTY',
    
    formatRegex = re.compile(r'(QTY|ITEM|TOTAL| ){5}',re.IGNORECASE)
    start_line = 100000000
    for i in range(len(receipt)):
        mo = re.search(formatRegex,receipt[i])
        if mo:
            print(i)
            print(mo.group(0))
            break
    '''
    
    #Manipulate the match object groups to obtain an ordering of the quantity, price and item

    #Match price to the correct item for every line
    
    priceRegex = re.compile(r'\d+\.\d\d')
    qtyRegex = re.compile(r'(\d+)\s')
    nonItemRegex = re.compile(r'total|change|cash|gst|amount',re.IGNORECASE)
    
    prev_line_has_price = False
    
    for line in receipt:

        #Search price first
        non_item_match = re.search(nonItemRegex,line)
        if non_item_match:
            if prev_line_has_price:
                prev_line_has_price = False
            continue
    
        price_match = re.search(priceRegex,line)
        
        if price_match:

            #Set variables
            prev_line_has_price = True
            quantity = 1
            
            #Search for quantity
            qty_match = re.search(qtyRegex,line)
            item = ""
            
            if qty_match:
                quantity = int(qty_match.group(1))
                item = line.replace(qty_match.group(0), '')
                
            item = item.replace(price_match.group(0),'')
            
            for i in range(quantity):
                itemdict = {'item':item,'price':price_match.group(0)}
                data.append(itemdict)
            #itemdict = {'item':item,'price':price_match.group(0),'qty':quantity}
            #data.append(itemdict)
            
        else:
            
            if prev_line_has_price:
                prev_line_has_price = False
                last_item = data[-1]
                last_item["item"] += (" " + line)
            else:
                continue
            
    return data
    

def main():

    message = get_lines(file,10)
    pp = pprint.PrettyPrinter()
    #pp.pprint(message)
    data = get_item_price_dict(message)
    pp.pprint(data)

if __name__ == '__main__':
    main()

