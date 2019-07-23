import logging
import os
from telegram.ext import *
from telegram import *

########## Logger ##############
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
########## Pretty Print ###########
import pprint
pp = pprint.PrettyPrinter(indent=4,width=20)
#pp.pprint(update.to_dict())

updater = Updater("token", use_context=True)
bot = telegram.Bot(token = "token")

data = {} #dictionary of dictionaries (user_id:item:price)
ITEM, PRICE, MANUAL = range(3)

def start(update, context):
    pp.pprint(update.to_dict())
    keyboard = [
                [InlineKeyboardButton("Send picture of receipt", callback_data='Pic' )],
                [InlineKeyboardButton("Input manually", callback_data='Manual'),
                InlineKeyboardButton("Help", callback_data='Help')],              
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_id = update._effective_chat.id
    data[user_id] = {}
    data[user_id]['prev_input'] = -1
    data[user_id]['item_list'] = {}
    data[user_id]['item_counter'] = 0 # to count the number of items
    
    update.message.bot.send_message(update.message.chat_id,'Welcome! \n''Please select an option: ',reply_markup=reply_markup)
    # Second type of keyboard 
    # update.message.reply_text('Welcome! \n''Please select an option: ',reply_markup=ReplyKeyboardMarkup(keyboard), one_time_keyboard=True)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # Add a handler to listen for the response of the button press
    
def button(update, context):
    pp.pprint(update.to_dict())
    query = update.callback_query
    #query.edit_message_text(text="Selected option: {} ".format(query.data))
    if query.data == 'Pic':
        query.edit_message_text("Selected option: {}\n".format(query.data) +
                                'Please send a picture of your reciept:')
        picture(update, context)

    elif query.data == 'Manual':
        """query.edit_message_text("Selected option: {}\n".format(query.data) +
                                "Manual input:",
                                )"""
        manual(update, context)
        
        
    elif query.data == 'Help':
        query.edit_message_text('Please choose either to: \n' +
                                '1. Take a picture of receipt\n' +
                                ' '*5 + 'or\n' +
                                '2. Key in the details manually \n\n' +
                                'Enter /start again to restart')
    else:
        context.bot.send_message(chat_id=query.message.chat_id, text="Please select a valid option")
        
"""def picture(update,context):
    updater.dispatcher.add_handler(MessageHandler(Filters.photo,picture))
    print('pic')
        #Send message 'Processing Receipt...'
    context.bot.send_message(chat_id=update.message.chat_id,text='Processing receipt...')
        #Retrieve the id of the photo with the largest size
    photo_file = context.bot.get_file(update.message.photo[-1].file_id)
        #Save path shows which directory to save photo to - EDIT ACCORDINGLY
    save_path = '/Users/daniel/Downloads/Orbital'
        #Create path with filename of photo
    filename = os.path.join(save_path,'{}.jpg'.format(photo_file.file_id))
        #Download photo to the specified file path
    photo_file.download(filename)
        #Send message to update user that receipt has been received
    context.bot.send_message(chat_id=update.message.chat_id,text='Receipt received!')
    ### TO ADD : remove handler"""

def cancel(update,context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Cancelled. Please press /start to start again',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def print_items(update,context):
    user_id = update._effective_chat.id
    for key, val in data[user_id]['item_list'].items() :
        print (key + ":" + val)  
                                            
            

def manual(update,context):
    #pp.pprint(update.to_dict())

    user_id = update._effective_chat.id
#    if "callback_query" in update:

    update.callback_query.edit_message_text("Please enter item number " +
                                            #str(data[user_id]['item_counter']+1) +
                                            str(int(len(data[user_id]['item_list'])+1)) +
                                            '\n' +
                                            "Items so far : \n" 
                                            #str(print_items(update,context))
                                            )
    """   else:
        update.message.reply_text(update.message.chat_id,
                                    "Please enter item number " +
                                            #str(data[user_id]['item_counter']+1) +
                                            str(int(len(data[user_id]['item_list'])+1)) +
                                            '\n' +
                                            "Items so far : \n" 
                                    )"""
                                        
    #update._effective_message.edit_text('test')
    #ForceReply(force_reply=True)
    print("\n manual \n" )
    #input_item(update,context)
    """EXP"""
    data[user_id]['bot_context'] = context
    data[user_id]['bot_update'] = update

    
    print(data)
    updater.dispatcher.add_handler(manual_input_items)
    
    return ITEM

def input_item(update,context):
    #pp.pprint(update.to_dict())
    user_id = update._effective_chat.id
    item_name = update.message.text
    
    data[user_id]['item_list'][item_name] = 0
    data[user_id]['item_counter'] += 1

    print("\n item is " + item_name)
    data[user_id]['prev_input'] = update.message.text
    print("\n")
    print(data[user_id])
    return PRICE
   
def input_price(update,context):
    #pp.pprint(update.to_dict())
    user_id = update._effective_chat.id
    """insert reply text : please enter "entry" price"""
    price = update.message.text
    item_name = data[user_id]['prev_input']
  
    print("\n price is " + price)
    data[user_id]['item_list'][item_name]=price
    
    data[user_id]['prev_input'] = update.message.text
    print('\n')
    print(data[user_id])
    #ConversationHandler.END
    #print("\n ended")
    manual(data[user_id]['bot_update'],data[user_id]['bot_context'])
    return ITEM

manual_input_items = ConversationHandler(
    entry_points = [MessageHandler(Filters.text, input_item)], ### Bug is here 
    states = {
        
        MANUAL : [MessageHandler(Filters.text, manual)],
        ITEM : [MessageHandler(Filters.text, input_item)],
        PRICE : [MessageHandler(Filters.text, input_price)]
        },
    fallbacks = [CommandHandler('cancel', cancel)]
    )

def sum_all(dic):
    total = 0
    for price in dic.values():
        total += price
    return total

my_dict = {'a':1, 'b':1, 'c':1}

def split_even(update,context):
    user_id = update._effective_chat.id
    #total_sum = sum_all(data[user_id]['item_list'])
    total_sum = sum_all(my_dict)
    #take in number of people
    bot.send_message(chat_id=update.message.chat_id, 
                 text="*bold* _italic_ `fixed width font`(How many people are there?).", 
                 parse_mode=telegram.ParseMode.MARKDOWN)


    #output total_sum / number of people 
    
    #SEND a message




    
    
### Commands 
def help(update, context):
    update.message.reply_text("Use /start to test this bot.")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

########################## Extra Functions ####################################################
def test(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
def wrong_command(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
def echo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
    
def caps(update, context):
    print("hello:)")
    text_caps = ' '.join(context.args).upper()
    print(text_caps)
    context.bot.send_message(chat_id=update.message.chat_id, text=text_caps)

### Inline Mode function 
def inline_caps(update, context):
    pp.pprint(update.to_dict())
    print("hello")
    query = update.inline_query.query
    if not query:
        return
    
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

############################## Extra Functions #################################################

def main():
    print(bot.getMe())
    # Make sure to set use_context=True to use the new context based callbacks
    updater.dispatcher.add_handler(CommandHandler('start', start))
    
    updater.dispatcher.add_handler(CommandHandler('split', split_even))
#############   EXTRA FUNCTIONS     #################
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(CommandHandler('caps', caps))
    updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))
#############   EXTRA FUNCTIONS     #################
    
    # Help Command
    updater.dispatcher.add_handler(CommandHandler('help', help))
    # Wrong Command
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, wrong_command)
                                
    # Log errors
    updater.dispatcher.add_error_handler(error)
    # Start Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
