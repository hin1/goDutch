import re
import os
import json
import pprint
from google.protobuf.json_format import MessageToJson
import ast
import operator

#file = '/Users/seanchan/goDutch/test/testpic3-full_response.txt' #MACS
file = '/Users/seanchan/goDutch/test/testpic4-text_annotation.txt' #BURGER KING    

#def upscan(item_dict,price_lines,start_line_num):
    

#proportion_threshold: how far to the right of the page
def is_price(number_coord, page_left, page_right, proportion_threshold):
    dist_left_edge_to_num = number_coord - page_left
    width = page_right - page_left
    if (dist_left_edge_to_num > (proportion_threshold*width)):
        return True
    else:
        return False
    
def fcombined_parse_and_regex(filename,threshold):

    #Statistically, 65% of times 8 is confused as B, and 47% of 0 as O
    priceRegex = re.compile(r'''(
                            (\d|B|O)+
                            \.
                            (\d|B|O){2})
                            ''',re.VERBOSE)
    qtyRegex = re.compile(r'\s*(\d+)\s(x)?')
    belowItemRegex = re.compile(r'(item|total|change|cash|gst|amount|ttl|service)',re.IGNORECASE)
    
    formatRegex = re.compile(r'(desc(ription)?|item|name|am(oun)?t|q(uanti)?ty|price|total){1,4}',re.IGNORECASE)
    aboveItemRegex = re.compile(r'cashier
    
    if (os.path.exists(filename)):
        with open(filename) as f:
             response = f.read()

        response = ast.literal_eval(response)

        #Find overall page bounds
        page_left = 0
        page_right = 0

        #Check file type and extract relevant information
        filetype = filename.split('-')[-1]
        if (filetype == "text_annotation.txt"):
            page_left = response[0]["bounding_poly"]["vertices"][0]["x"]
            page_right = response[0]["bounding_poly"]["vertices"][1]["x"]
            receipt = response[1:] #Take away the first element, which is the entire string
        elif (filetype == "full_response.txt"):
            receipt = response["text_annotations"]
            page_left = receipt[0]["bounding_poly"]["vertices"][0]["x"]
            page_right = receipt[0]["bounding_poly"]["vertices"][1]["x"]
            receipt = receipt[1:] #Take away the first element, which is the entire string


        '''GET LINES OF RECEIPT'''
        
        # bounding_poly order is: top left, top right, bottom right, bottom left
        words = []
        message = []
        price_lines = []
        
        for element in receipt:
            vertices = element["bounding_poly"]["vertices"]
            avg_y_coord = (vertices[3]["y"] + vertices[0]["y"])/2
            avg_x_coord = (vertices[3]["x"] + vertices[0]["x"])/2
            # each word represented as vertical, horizontal, then content
            words.append([avg_y_coord,avg_x_coord, element["description"]])

        words = sorted(words)
        
        #Align vert coords of words on the same line
        prev_line = words[0][0] #y-coord of first word
        for word in words:
            if ((word[0] - prev_line) < threshold):
                word[0] = prev_line
            else:
                prev_line = word[0]
                
        words = sorted(words,key=operator.itemgetter(0,1))

        #Get message as list of lines
        prev_line = words[0][0]
        line = ""
        for word in words:
            if (word[0] == prev_line):
                line += " "
                line += word[2]         
            else:
                message.append(line)
                line = word[2]
                
            prev_line = word[0]

            match_price = re.search(priceRegex,word[2])
            match_non_item = re.search(nonItemRegex,line)
            
            if (match_non_item):
                continue
            
            if (is_price(word[1],page_left,page_right,0.75) and match_price):
                price_lines.append(len(message))

        for i in range(price_lines[-1],len(message)):
            match_price2 = re.search(priceRegex,message[i])
            match_total = re.search(nonItemRegex,message[i])
            if match_total and match_price2:
                price_lines.append(i)
                break
                
        return message

    

        '''REGEX'''
        data = {}
        scan-direction = 0 #if scan-direction: 1 -> up, 2 -> down
        line_continue = price_lines[0]

        #All items single line
        if (sorted(price_lines) == list(range(min(price_lines), max(price_lines)+1)):
            
            for i in range(len(price_lines)):
            
                if (price_lines[i] == price_lines[-1]):
                    break
            
                line_num = price_lines[i]
                line = message[line_num]
                
                price_match = re.search(priceRegex,line)
                price = price_match.group(0)
                price = float(price.replace('B','8').replace('O','0'))

                qty_match = re.search(qtyRegex,line)

                

        for i in range(len(price_lines)):

            line_continue = i

            if (price_lines[i] == price_lines[-1]):
                break
            
            line_num = price_lines[i]
            line = message[line_num]
                   
            qty_match = re.search(qtyRegex,line)
            
            price_match = re.search(priceRegex,line)
            price = price_match.group(0)
            price = float(price.replace('B','8').replace('O','0'))
            
            if qty_match:
                
                quantity = int(qty_match.group(1))
                item = line.replace(qty_match.group(0), '')
                item = item.replace(price_match.group(0),'')
                
                if ((line_num + 1) in price_lines):
                    #up or down/single line
                    #put in normally
                    for each in range(quantity):
                        data[item] = price
                        #print(item)
                    continue
                
                else:
                    #down
                    for j in range(line_num+1,price_lines[i+1]):
                        item += " "
                        item += message[j]
                    for each in range(quantity):
                        data[item] = price
                        print(item)
                    
            else:
                #up
                #if first one, then stop when qty detected
                item = line.replace(price_match.group(0),'')
                for j in range(line_num-1,0,-1):
                    line = message[j]
                    qty_match2 = re.search(qtyRegex,message[j])
                    if qty_match2:
                        quantity = int(qty_match2.group(1))
                        item = line.replace(qty_match2.group(0), '') + " " + item
                        #print(item)
                        for each in range(quantity):
                            data[item] = price
                        break
                    else:
                        item = line + " " + item
                        
        return data
            
    else:
        print("File does not exist.")

#For files
def fget_vert_coord_to_lines(filename,threshold):

    pp = pprint.PrettyPrinter()
    
    if (os.path.exists(filename)):
        with open(filename) as f:
             response = f.read()

        response = ast.literal_eval(response)

        #Find overall page bounds
        page_left = 0
        page_right = 0

        #Check file type and extract relevant information
        filetype = filename.split('-')[-1]
        if (filetype == "text_annotation.txt"):
            page_left = response[0]["bounding_poly"]["vertices"][0]["x"]
            page_right = response[0]["bounding_poly"]["vertices"][1]["x"]
            receipt = response[1:] #Take away the first element, which is the entire string
        elif (filetype == "full_response.txt"):
            receipt = response["text_annotations"]
            page_left = receipt[0]["bounding_poly"]["vertices"][0]["x"]
            page_right = receipt[0]["bounding_poly"]["vertices"][1]["x"]
            receipt = receipt[1:] #Take away the first element, which is the entire string

        # bounding_poly order is: top left, top right, bottom right, bottom left
        words = []
        for element in receipt:
            vertices = element["bounding_poly"]["vertices"]
            avg_y_coord = (vertices[3]["y"] + vertices[0]["y"])/2
            avg_x_coord = (vertices[3]["x"] + vertices[0]["x"])/2
            # each word represented as vertical, horizontal, then content
            words.append([avg_y_coord,avg_x_coord, element["description"]])

        words = sorted(words)
        
        #Align vert coords of words on the same line
        prev_line = words[0][0] #y-coord of first word
        for word in words:
            if ((word[0] - prev_line) < threshold):
                word[0] = prev_line
            else:
                prev_line = word[0]
        words = sorted(words,key=operator.itemgetter(0,1))
        
        message = []

        prev_line = words[0][0]
        line = ""
        for word in words:
            if (word[0] == prev_line):
                line += " "
                line += word[2]
            else:
                message.append(line)
                line = word[2]
            prev_line = word[0]

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
Data Structure (Dictionary):
    {'item1':price1,
    'item2':price2
    ...}
'''
def get_item_price_dict(receipt):

    data = []
    
    #Manipulate the match object groups to obtain an ordering of the quantity, price and item

    #Match price to the correct item for every line
    
    priceRegex = re.compile(r'\d+\.\d\d')
    qtyRegex = re.compile(r'\s*(\d+)\s(x)?')
    nonItemRegex = re.compile(r'total|change|cash|gst|amount',re.IGNORECASE)
    
    prev_line_has_price = False
    
    for line in receipt:

        #Reset prev_line_has_price if no longer looking at the same item
        non_item_match = re.search(nonItemRegex,line)
        if non_item_match:
            if prev_line_has_price:
                prev_line_has_price = False
            continue
        
        #Search price first
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

    #message = fget_vert_coord_to_lines(file,15)
    #message = get_lines(file,10)
    message = fcombined_parse_and_regex(file,15)
    pp = pprint.PrettyPrinter()
    pp.pprint(message)
    #data = get_item_price_dict(message)
    #pp.pprint(data)

if __name__ == '__main__':
    main()

