import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters,InlineQueryHandler
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
########## Pretty Print ###########
import pprint
pp = pprint.PrettyPrinter(indent=4,width=20)

updater = Updater("728096945:AAEqL7_eozmm_33rFT4QDc1y2V6c_PMlbKc", use_context=True)
data = {} #dictionary of list of dictionaries (user_id:[item:price])
counter = 1

def start(update, context):
    keyboard = [
                [InlineKeyboardButton("Send picture of receipt", callback_data='Pic' )],
                [InlineKeyboardButton("Input manually", callback_data='Manual'),
                InlineKeyboardButton("Help", callback_data='Help')],
                #[InlineKeyboardButton("chat",callback_data='hello')]              
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_id = update._effective_chat.id
    data[user_id] = []
    print(data[user_id])
    
    #pp.pprint(update.to_dict())
    update.message.reply_text('Welcome! \n''Please select an option: ',reply_markup=reply_markup)
    # update.message.reply_text('Welcome! \n''Please select an option: ',
    #                          reply_markup=ReplyKeyboardMarkup(keyboard), one_time_keyboard=True)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
def button(update, context):
    query = update.callback_query
    #query.edit_message_text(text="Selected option: {} ".format(query.data))
    if query.data == 'Pic':
        query.edit_message_text("Selected option: {}\n".format(query.data) +
                                'Please send a picture of your reciept:'
                                )
        picture(update, context)

    elif query.data == 'Manual':
        #query.edit_message_text("Selected option: {}\n".format(query.data) +
        #                        "Manual input:",
        #                        )
        manual(update, context)
        
    elif query.data == 'Help':
        query.edit_message_text('Please choose either to: \n' +
                                '1. Take a picture of receipt\n' +
                                ' '*5 + 'or\n' +
                                '2. Key in the details manually \n\n' +
                                'Enter /start again to restart')
        #context.bot.send_message(chat_id=query.message.chat_id, text="Help is on the way")
    else:
        context.bot.send_message(chat_id=query.message.chat_id, text="Please select a valid option")
        
def picture(update,context):
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

    ### TO ADD : remove handler 


def manual(update,context,*entry):
    #pp.pprint(update.to_dict())
    user_id = update._effective_chat.id
    update.callback_query.edit_message_text("Please enter item no. " + str(counter)
                                            )
    
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, input_entries))  

    #user = update.callback_query
    #pp.pprint(user.to_dict()['from']['first_name'])   
    #pp.pprint(update.to_dict())
    
    #text_caps = ' '.join(context.args).upper()
    #print(text_caps)
    #context.bot.send_message(chat_id=update.message.chat_id, text=text_caps)

    #query = update.message.text
    #query = update.inline_query.query
    """if not query:
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
    
    #logger.info("Item of %s: %s", user.first_name, update.message.text)
    #List.append(update.message.text)
    #context.bot.send_message(chat_id=query.message.chat_id, text="Please enter item name")
    #logger.info("Price of %s: %s", user.first_name, update.message.text)
    #context.bot.send_message(chat_id=query.message.chat_id, text="Please enter item value")"""
def input_entries(update,context):
    user_id = update._effective_chat.id
    #input_item()
    #input_price()
    
    item_name = update.message.text
    item = {}
    #my_dict
    """insert reply text : please enter "entry" price"""
    #pp.pprint(update.to_dict())
    #print(entry)
    
    item[item_name]=input_price(update,context)
    data[user_id].append(item)
    print(data[user_id])
    
def input_price(update,context):
    print("input price")
    price = 10
    print(price)
    return(price) 
    
    
######################### Commands ########################

def help(update, context):
    update.message.reply_text("Use /start to test this bot.")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

########################## Extra Functions ###########################
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

########################## Inline Mode functions #####################
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

############################## Extra Functions #######################


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    
    #updater.dispatcher.add_handler(CallbackQueryHandler(manual))

   
    
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(CommandHandler('caps', caps))
    updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))

    # Help Command
    updater.dispatcher.add_handler(CommandHandler('help', help))
    # Wrong Command
    updater.dispatcher.add_handler(MessageHandler(Filters.command, wrong_command))
    # Log errors
    updater.dispatcher.add_error_handler(error)
    # Start Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
