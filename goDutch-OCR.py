'''
------------------------
goDutch - OCR algorithm
1. Receive update from user in the form of a photo after selecting relevant commmand
2. Send the photo to the Azure server in order to conduct OCR
3. Convert json object returned to string form and send message back in response to user
-----------------------
'''

'''
******IMPORTED MODULES******
'''

import telegram
import json as js
import re
import string
import os
import requests
import time

'''
import cv2
import operator
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
#%matplotlib inline
'''

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

#Photo to OCR
#filename = '/Users/seanchan/Downloads/testreceipt.jpeg'

'''
******MICROSOFT AZURE******
'''

#Variables for REST API
_url = 'https://southeastasia.api.cognitive.microsoft.com/vision/v2.0/ocr?language=en&detectOrientation=true'
_key = '4ca1a3b2c2e946f4af8c1d830ebe6eaa'
_maxNumRetries = 10

def processRequest(json,data,headers,params):
        retries = 0
        result = None

        while True:
                response = requests.request('post', _url, json=json, data=data, headers=headers, params = params)

                if response.status_code == 429: #429 Too Many Requests
                        print("Message: %s" % (response.json() ) )
                        if retries <= _maxNumRetries:
                                time.sleep(1)
                                retries += 1
                                continue
                        else:
                                print("Error: failed after retrying!")
                                break
                elif response.status_code == 200: #200 OK
                        result = response.json()
                        print(js.dumps(result,indent=4))
                else: #Other status code
                        print("Error code: %d" % (response.status_code) )
                        print("Message: %s" % (response.json()) )
                break
        return result

#Parameters: operationLocation to get text result, subscription key
def getOCRTestResult(operationLocation, headers):
        retries = 0
        result = None

        while True:
                response = requests.requests('get',operationLocation,json=None,data=None,headers=headers,params=None)

                if response.status_code == 429: #429 - Too Many Requests
                        print("Message: %s" % (response.json()) )
                        if retries <= _maxNumRetries:
                                time.sleep(1)
                                retries += 1
                                continue
                        else:
                                print("Error: failed after retrying!")
                                break
                elif response.status_code == 200: #200 - OK
                        result = response.json()
                else: #Other status code
                        print("Error code: %d" % (response.status_code) )
                        print("Message: %s" % (response.json()) )
                break
        return result


'''
******BOT FUNCTIONS*******
'''

#Bot functions
'''
def start(update,context):
	context.bot.send_message(chat_id=update.message.chat_id,text="I'm a bot, please talk to me!")
	
def echo(update,context):
	context.bot.send_message(chat_id=update.message.chat_id,text=update.message.text)

def caps(update,context):
	text_caps = ' '.join(args).upper()
	context.bot.send_message(chat_id=update.message.chat_id,text=text_caps)
'''


def ocr(update,context):
        context.bot.send_message(chat_id=update.message.chat_id,text='Processing receipt...')
        photo_file = context.bot.get_file(update.message.photo[-1].file_id)
        save_path = '/Users/seanchan/Documents/Orbital/'
        #filename saved for use for Azure API later
        filename = os.path.join(save_path,'{}.jpg'.format(photo_file.file_id))
        photo_file.download(filename)
        context.bot.send_message(chat_id=update.message.chat_id,text='Receipt received!')

        #Load raw image file
        if not os.path.exists(filename):
                print('Error, file does not exist!')
        else:
                #Set parameters for REST API
                f = open(filename,'rb')
                data = f.read()
                headers = {'Ocp-Apim-Subscription-Key':'4ca1a3b2c2e946f4af8c1d830ebe6eaa','Content-Type':'application/octet-stream'}
                params = {'handwriting':'false'}
                json = None

                #Post request to Azure server
                message = processRequest(json,data,headers,params)
                print('Request processed!')
                context.bot.send_message(chat_id=update.message.chat_id,text='Request processed!')

                #Retrieve text

'''
MAIN FUNCTION
'''

def main():             

        #Initialise the bot, updater and dispatcher
        updater = Updater(token="792177430:AAGEslM_BD3S7jDZa7kr1GHmaaBA5d2vJXI",use_context=True)
        dispatcher = updater.dispatcher

        #Adding handlers
        '''
        start_handler = CommandHandler('start',start)
        echo_handler = MessageHandler(Filters.text,echo)
        caps_handler = CommandHandler('caps',caps,pass_args=True)
        '''
        ocr_handler = MessageHandler(Filters.photo,ocr)

        '''
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(echo_handler)
        dispatcher.add_handler(caps_handler)
        '''
        dispatcher.add_handler(ocr_handler)

        #Polling
        updater.start_polling()
        updater.idle()
        
        '''
        AZURE PROCESSING

        Requirements for request:
        1. Request body (image format)
        2. Request parameters (dictionary with key 'handwriting')
        3. Request headers (dictionary with keys 'Content-Type' [tells string media type
           of body sent to API] and 'Ocp-Apim-Subscription-Key' [Subscription key of Azure]
        4. Request URL (URL to send image to process)

        '''
        '''
        #Load raw image file
        if not os.path.exists(filename):
                print('Error, file does not exist!')
        else:
                #Set parameters for REST API
                f = open(filename,'rb')
                data = f.read()
                headers = {'Ocp-Apim-Subscription-Key':'4ca1a3b2c2e946f4af8c1d830ebe6eaa','Content-Type':'application/octet-stream'}
                params = {'handwriting':'false'}
                json = None

                #Post request to Azure server
                #operationLocation = processRequest(json,data,headers,params)
                message = processRequest(json,data,headers,params)
                print('Request processed!')
                

                
                #Get JSON object from Azure server
                result = None
                if (operationLocation != None):
                        #headers = {}
                        #headers['Ocp-Apim-Subscription-Key'] = _key
                        iteration = 0
                        while True:
                                time.sleep(1)
                                iteration += 1
                                print('Iteration: {}'.format(iteration))
                                result = getOCRTextResult(operationLocation, headers)
                                if result['status'] == 'Succeeded' or result['status'] == 'Failed':
                                        break
                
                
                #Retrieve text (TO BE EDITED)
                lines = result['recognitionResult']['lines']
               
                items = []  #list of dictionaries
                text = []
                for i in range(len(lines)):
                        words = lines[i]['words']
                        for j in range(len(words)):
                                text.append(words[j]['text']

                #Identify name, qty and price

                items.append({'name': name ,'qty': qty,'u_price': u_price})
        '''                                

if __name__ == '__main__':
        main()
        

        
        
