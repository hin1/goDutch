import re
import os
import json
import pprint
from google.protobuf.json_format import MessageToJson
import ast
import operator

#file = '/Users/seanchan/goDutch/test/testpic3-full_response.txt' #MACS
file = '/Users/seanchan/goDutch/test/testpic4-text_annotation.txt' #BURGER KING    

formatRegex = re.compile(r'(desc(ription)?|item|name|am(oun)?t|q(uanti)?ty|price|total){1,4}',re.IGNORECASE)
format2Regex = re.compile(r'''
                            \s?.*?
                            (
                            qty|quantity
                            amt|amount|price|total
                            )
                            \s?.*?
                            ''',re.IGNORECASE|re.VERBOSE) #USE FINDALL FOR THIS

aboveItemRegex = re.compile(r'''
                            (cashier|gst|table|bill|to\ go|take\ away|tel|fax|inv(oice)?|tax|receipt|check)|
                            (\d\d:\d\d(:\d\d)?)|
                            (\d\d(/|-)\d\d(/|-)\d\d(\d\d)?)
                            ''',re.IGNORECASE|re.VERBOSE)
belowItemRegex = re.compile(r'(item|to?ta?l|change|cash|gst|amount|service|tot)',re.IGNORECASE)

itemformatRegex = re.compile(r'(desc(ription)?|item|name)',re.IGNORECASE)
priceformatRegex = re.compile(r'(price|am(oun)?t)',re.IGNORECASE)
totalformatRegex = re.compile(r'(total)',re.IGNORECASE)
qtyformatRegex = re.compile(r'(q(uanti)?ty)',re.IGNORECASE)

#Statistically, 65% of times 8 is confused as B, and 47% of 0 as O
priceRegex = re.compile(r'''(
                        (\d|B|O)+
                        \.
                        (\d|B|O){2}
                        )''',re.VERBOSE)

qtyRegex = re.compile(r'''
                    (
                    \s
                    (x|\*)
                    \s?
                    (\d|B|O)+
                    )|
                    
                    (
                    (\d|B|O)+
                    \s?
                    (x|\*)
                    \s
                    )|

                    (
                    \s
                    (\d|B|O)+
                    (\.(0|O)*)?
                    \s
                    )
                    ''',re.VERBOSE)
gstRegex = re.compile(r'(gst|tax|vat):?\ ',re.IGNORECASE)
servicechargeRegex = re.compile(r'(s(er)?vi?ce? ch(ar)?ge?)|(s(\.|\ )?c(\.|\ )?:?\ )',re.IGNORECASE)
inclusiveRegex = re.compile(r'incl?(usive|uding|ude)?(:|\.)?\ ',re.IGNORECASE)

numRegex = re.compile(r'^(\d|B|O)+$')
                   
def get_dup_regex(item):
    duplicateRegex = re.compile(re.escape(item) + r'(\ ~(\d+))?$')
    return duplicateRegex

#proportion_threshold: how far to the right of the page
def is_price(number_coord, page_left, page_right, proportion_threshold):
    dist_left_edge_to_num = number_coord - page_left
    width = page_right - page_left
    if (dist_left_edge_to_num > (proportion_threshold*width)):
        return True
    else:
        return False

def fget_raw_annotation(filename,threshold):
    
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

    else:
        print("File does not exist.")

    return receipt, page_left, page_right

def get_price_lines(receipt, threshold, page_left, page_right):
    
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
        match_non_item = re.search(belowItemRegex,line)
        
        if (match_non_item):
            continue

        #Condition: 1 -> price is located far right, 2 -> matches price regex, 3 -> no duplicates
        if (is_price(word[1],page_left,page_right,0.6) and match_price and (len(message) not in price_lines)):
            price_lines.append(len(message))

    return message, price_lines

def setup_regex(price_lines,message):
    
    #Find top line and order
    order = []
    
    for line_num1 in range(price_lines[0]-1,0,-1):
        order = formatRegex.findall(message[line_num1])
        if order:
            price_lines.insert(0,line_num1)
            break
            
        else:
            match_top = aboveItemRegex.search(message[line_num1])
            if match_top:
                price_lines.insert(0,line_num1)
                break
            else:
                continue
            
    if (order == []):
        order = ['quantity','price']
    else:
        if (('price' and ('amt' or 'amount')) in order):
                try:
                    order[order.index('amount')] = 'total'
                except:
                    order[order.index('amt')] = 'total'
        if ('price' or 'amount' or 'amt' or 'total') not in order:
            order.append('price')
        if ('total' in order) and (('price' or 'amount' or 'amt') not in order):
            order[order.index('total')] = 'price'

    order.append('item') #Add item manually because last to consider

    #Find bottom line
    for line_num2 in range(price_lines[-1],len(message)):
        match_bottom = re.search(belowItemRegex,message[line_num2])
        if match_bottom:
            price_lines.append(line_num2)
            break

    #Check alignment of price with item
    align = 0
    #if align: 1 -> top, -1 -> bottom, 0 -> single line
    #Check if price lines are consecutive
    if (sorted(price_lines) == list(range(min(price_lines), max(price_lines)+1))):
        align = 0
    else:
        #Check if price line is right after top line
        if (price_lines[1] == price_lines[0] + 1): #Potential major bug
            align = 1
        else:
            align = -1

    return align,order,price_lines

'''
Data Structure (Dictionary):
    {'item1':price1,
    'item2':price2
    ...}
'''
def get_item_price(align,order,price_lines,message):
    
    data = {}

    #Single line
    if align == 0:
        for i in range(1, len(price_lines)-1):
            line = message[price_lines[i]]
            for element in order:

                price = 0.0
                quantity = 1
                item = ""
                
                if priceformatRegex.search(element):
                    price_match = priceRegex.search(line)
                    price = price_match.group(0)
                    price = float(price.replace('B','8').replace('O','0'))
                    line = line.replace(price_match.group(0),'')
                          
                elif qtyformatRegex.search(element):
                    qty_match = qtyRegex.search(line)
                    if qty_match:
                        for cg in qty_match.groups():
                            if cg == None:
                                continue
                            match = numRegex.search(cg)
                            if match: quantity = int(match.group().replace('B','8').replace('O','0'))
                        line = line.replace(qty_match.group(0), '')

                elif totalformatRegex.search(element):
                    total_match = priceRegex.search(line)
                    if total_match:
                        line = line.replace(total_match)
                    
                elif itemformatRegex.search(element):
                    item = line

            #Numbering duplicate items
            dup_start_num = 0
            for entry in data:
                duplicateRegex = get_dup_regex(item)
                dup_match = duplicateRegex.search(entry)
                if dup_match:
                    if dup_match.group(2) == None:
                        dup_start_num = 1
                        break
                    else:
                        dup_start_num = int(dup_match.group(2))
                        break

            for each in range(quantity):
                copy_num = dup_start_num + each
                if (copy_num == 0):
                    data[item] = price
                else:
                    data[item + " ~" + str(copy_num)] = price
    
    #Top alignment
    elif align == 1:
        #Scan first price line to bottom line
        for i in range(1, len(price_lines)):
            
            price = 0.0
            quantity = 1
            item = ""

            for j in range(price_lines[i],price_lines[i+1]):

                line = message[price_lines[j]]
                orig_order = order.copy()
                dup_order = order.copy() #Create duplicate order
        
                for element in orig_order:
                    
                    if priceformatRegex.search(element):
                        price_match = priceRegex.search(line)
                        price = price_match.group(0)
                        price = float(price.replace('B','8').replace('O','0'))
                        line = line.replace(price_match.group(0),'')
                        dup_order.remove(element)
                              
                    elif qtyformatRegex.search(element):
                        qty_match = qtyRegex.search(line)
                        if qty_match:
                            for cg in qty_match.groups():
                                if cg == None:
                                    continue
                                match = numRegex.search(cg)
                                if match: quantity = int(match.group().replace('B','8').replace('O','0'))
                            line = line.replace(qty_match.group(0), '')
                            dup_order.remove(element)

                    elif totalformatRegex.search(element):
                        total_match = priceRegex.search(line)
                        if total_match:
                            line = line.replace(total_match)
                            dup_order.remove(element)
                        
                    elif itemformatRegex.search(element):
                        item = item + " " + line

                    orig_order = dup_order
                    
            dup_start_num = 0
            for entry in data:
                duplicateRegex = get_dup_regex(item)
                dup_match = duplicateRegex.search(entry)
                if dup_match:
                    if dup_match.group(2) == None:
                        dup_start_num = 1
                        break
                    else:
                        dup_start_num = int(dup_match.group(2))
                        break

            for each in range(quantity):
                copy_num = dup_start_num + each
                if (copy_num == 0):
                    data[item] = price
                else:
                    data[item + " ~" + str(copy_num)] = price
                
            if (price_lines[i+1] == price_lines[-1]):
                break

    #Bottom alignment
    elif align == -1:
        
        #Scan from top line to last price line
        for i in range(1, len(price_lines)-1):

            price = 0.0
            quantity = 1
            item = ""

            #Evaluate single item
            #From line right after price line to the next price line
            for j in range(price_lines[i-1]+1,price_lines[i]+1):
                
                line = message[j]
                orig_order = order.copy()
                dup_order = order.copy() #Create duplicate order
                
                #print(str(j) + ": " + line)
                #print(orig_order)

                for element in orig_order:

                    #print(line)
                    
                    if priceformatRegex.search(element):
                        price_match = priceRegex.search(line)
                        if price_match:
                            price = price_match.group(0)
                            price = float(price.replace('B','8').replace('O','0'))
                            line = line.replace(price_match.group(0),'')
                            dup_order.remove(element)
                              
                    elif qtyformatRegex.search(element):
                        qty_match = qtyRegex.search(line)
                        if qty_match:
                            for cg in qty_match.groups():
                                if cg == None:
                                    continue
                                match = numRegex.search(cg)
                                if match: quantity = int(match.group().replace('B','8').replace('O','0'))
                            line = line.replace(qty_match.group(0), '')
                            dup_order.remove(element)

                    elif totalformatRegex.search(element):
                        total_match = priceRegex.search(line)
                        if total_match:
                            line = line.replace(total_match)
                            dup_order.remove(element)
                        
                    elif itemformatRegex.search(element):
                        item = item + " " + line
                        #print("item" + item)

                    else:
                        print("Invalid format for " + element)

                    orig_order = dup_order
                
            dup_start_num = 0
            for entry in data:
                duplicateRegex = get_dup_regex(item)
                dup_match = duplicateRegex.search(entry)
                if dup_match:
                    if dup_match.group(2) == None:
                        dup_start_num = 1
                        break
                    else:
                        dup_start_num = int(dup_match.group(2))
                        break

            for each in range(quantity):
                copy_num = dup_start_num + each
                if (copy_num == 0):
                    data[item] = price
                else:
                    data[item + " ~" + str(copy_num)] = price

        return data

def get_misc(price_lines,message,data):

    gst_included = False
    
    for i in range(price_lines[-1],len(message)):
        
        line = message[i]
        price_match = priceRegex.search(line)
        
        if price_match:
            price = price_match.group(0)
            price = float(price.replace('B','8').replace('O','0'))
            if gstRegex.search(line):
                if inclusiveRegex.search(line):
                    gst_included = True
                else:
                    data['gst'] = price
            elif servicechargeRegex.search(line):
                data['service charge'] = price
            else:
                #print('No GST or service charge for line ' + str(i))
                continue
            
    return data

def fcombined_parse_and_regex(filename,threshold):

    '''EXTRACT TEXT ANNOTATION FROM RESPONSE'''

    receipt, page_left, page_right = fget_raw_annotation(filename,threshold)

    '''GET LINES OF RECEIPT'''
    
    message, price_lines = get_price_lines(receipt, threshold, page_left, page_right)
    
    '''SETUP REGEX'''
    
    align, order, price_lines = setup_regex(price_lines,message)

    '''REGEX'''

    data = get_item_price(align,order,price_lines,message)
    data = get_misc(price_lines,message,data)

    return data

def combined_parse_and_regex(response,threshold):

    '''EXTRACT TEXT ANNOTATION FROM RESPONSE'''

    page_left = response[0]["bounding_poly"]["vertices"][0]["x"]
    page_right = response[0]["bounding_poly"]["vertices"][1]["x"]
    receipt = response[1:]

    '''GET LINES OF RECEIPT'''
    
    message, price_lines = get_price_lines(receipt, threshold, page_left, page_right)
    
    '''SETUP REGEX'''
    
    align, order, price_lines = setup_regex(price_lines,message)

    '''REGEX'''

    data = get_item_price(align,order,price_lines,message)
    data = get_misc(price_lines,message,data)

    return data
      







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
    '''    
    else:
        print("File does not exist.")
    '''

#TO CHANGE
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

def get_raw_annotation(response,threshold):
    
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


'''
def main():

    pp = pprint.PrettyPrinter()

    #message = fget_vert_coord_to_lines(file,15)
    #message = get_lines(file,10)
    message = fcombined_parse_and_regex(file,15)
    pp.pprint(message)
    #data = get_item_price_dict(message)
    #pp.pprint(data)

if __name__ == '__main__':
    main()
'''
