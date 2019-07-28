import modules.google_regex as regex
import modules.google_ocr as ocr
import pprint
#import modules.menu as menu
#from modules.BOT_TOKEN import TOKEN
import os
import logging
from telegram.ext import *
from telegram import *

TOKEN = "TOKEN"
PORT = int(os.environ.get('PORT', '8443'))
updater = Updater(TOKEN,use_context=True)
# add handlers


print(TOKEN)
#pp = pprint.PrettyPrinter()

#updater = menu.Updater(menu.TOKEN, use_context=True)
bot = Bot(token = TOKEN)

#def main():

 #   file = '/Users/seanchan/goDutch/test/testpic4.jpeg'

  #  response_dict = ocr.get_full_response_dict(file)
   # data = regex.combined_parse_and_regex(response_dict,15)
   # pp.pprint(data)






#from modules.BOT_TOKEN import TOKEN

### Logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
### Pretty Print
import pprint
pp = pprint.PrettyPrinter(indent=4,width=20)
#pp.pprint(update.to_dict())
#updater = Updater(TOKEN, use_context=True)
#bot = Bot(token = TOKEN)
data = {}                                                                       # Dictionary of dictionaries (user_id:item:price)
ITEM, PRICE, MANUAL, SPLITEVEN, NAMES, DUTCH, PIC = range(7)                       # For convo handler for manual input of items


def start(update, context):
    #pp.pprint(update.to_dict())
    user_id = update._effective_chat.id
    data[user_id] = {}
    data[user_id]['prev_input'] = -1
    data[user_id]['item_list'] = {}
    data[user_id]['item_counter'] = 0                                           # To count the number of items

    keyboard = [
                [KeyboardButton("Send a Photo of Receipt")],
                [KeyboardButton("Input Items Manually"), KeyboardButton("Help")],
                ]


    update.message.reply_text('Hello! \n''Please select an option: ',
                              reply_markup=ReplyKeyboardMarkup(keyboard),
                              one_time_keyboard=True)

    updater.dispatcher.add_handler(pic_or_manual)                          # Handler to listen for manual input of items
    # TODO: Add handler to listen for Photo response
    # TODO: Add handler to listen for Help response




def manual_input(update,context):

    bot.send_message(chat_id=update._effective_chat.id,
            text="Please enter item:",
                 ForceReply = True,
                 reply_markup=ReplyKeyboardRemove()
                )
    return ITEM

def input_item(update,context):
    user_id = update._effective_chat.id
    item_name = update.message.text

    data[user_id]['item_list'][item_name] = 0
    data[user_id]['item_counter'] += 1

    bot.send_message(chat_id=update._effective_chat.id,
                 text="Please enter price of " + item_name,
                 ForceReply = True,
                 reply_markup=ReplyKeyboardRemove()
                )

    print("\nitem is " + item_name)
    data[user_id]['prev_input'] = update.message.text
    print(data[user_id])
    # TODO: deal with duplicates - python dictionary cannot deal with duplicates
            # Either use spaces or blank characters or (1),(2),(3) etc...
            # Take in GST and Service Charge
    return PRICE

def input_price(update,context):
    user_id = update._effective_chat.id
    price = update.message.text

    item_name = data[user_id]['prev_input']

    print("\nprice is " + price)
    data[user_id]['item_list'][item_name] = price
    data[user_id]['prev_input'] = update.message.text                               # May not need
    print(data[user_id])

    bot.send_message(chat_id=update._effective_chat.id,
                 text= "*{}*".format(str(data[user_id]['item_counter']))
                     + " *item(s) so far:*\n"
                     + "`{}`".format(enumerate_items(data[user_id]['item_list']))
                     + "\nContinue entering the next item or "+
                     "\nClick /done when you are done" +
                     "\nTo cancel, click /cancel",
                     parse_mode=ParseMode.MARKDOWN,

                 ForceReply = True,
                 reply_markup=ReplyKeyboardRemove(),
                )

    # TODO: Reject non float/ int inputs and repeat input price
    # TODO: Make the plural for 'item(s)' dynamic
    return ITEM

def enumerate_items(dic):
    text_width = 30                                                                 #To change based on device width
    output = "Item:" + (text_width-len("Item:"))*" " + "Price($):\n"
    for key, val in dic.items() :
        output += key + " "*(text_width-len(key)) + val + '\n'
    return output
    # TODO: Make text_width dynamic and based on device
    # TDOD: Deal with strings that are too long - truncate them?

def cancel(update,context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    update.message.reply_text('Cancelled. Please press /start to start again',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def man_done(update,context):
    user = update.message.from_user
    logger.info("User %s done with manual list input.", user.first_name)

    keyboard = keyboard = [
                [KeyboardButton("GoDutch"), KeyboardButton("Split Even")],              # Left-Right or Up-Down button layout?
                ]

    update.message.reply_text('Done!\n'+
                              'Do you want to GoDutch or split even ?',
                              reply_markup=ReplyKeyboardMarkup(keyboard),
                              one_time_keyboard=True
                              )
    updater.dispatcher.add_handler(split_method)
    return ConversationHandler.END

def end(update, context):
    user = update.message.from_user
    logger.info("User %s has ended GoDutch", user.first_name)
    print("end")
    update.message.reply_text('Thank you for using GoDutch!\nPlease press /start to start again',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def split(update, context):
    print("split even selected")
    user_id = update._effective_chat.id
    total_sum = sum_all(data[user_id]['item_list'])
    data[user_id]['total_sum'] = total_sum
    print("total sum is " + str(total_sum))
    bot.send_message(chat_id=update._effective_chat.id,
                 text="How many people is splitting?",
                 ForceReply = True,
                 reply_markup=ReplyKeyboardRemove())

    return SPLITEVEN

def get_no_of_people(update,context):
    user_id = update._effective_chat.id
    no_of_people = float(update.message.text)
    answer = data[user_id]['total_sum'] / no_of_people
    print("final answer is " + str(answer))
    ans = float('{:.2f}'.format(answer))                                                # Gets format to 2 d.p
    ans2= round(answer,2)
    print(ans)
    print(ans2)

    bot.send_message(chat_id=update.message.chat_id,
                 text= "Each person needs to pay: $"+ "{:.2f}".format(answer),
                 reply_markup=ReplyKeyboardRemove()
                     )
    end(update,context)
    return ConversationHandler.END

def sum_all(dic):
    total = 0
    for price in dic.values():
        total += float(price)
    return total






a= {"apples":{"price":1, "people":[]},
    "bannna":{"price":2, "people":[]},
    "cherry":{"price":3, "people":[]},
    "durians":{"price":4, "people":[]}
    }
                                        # To remove after testing Dummy list

names=[]                                # list of names to reuse

b= {"apples":{"price":1, "people":[]},
    "bannna":{"price":2, "people":[]},
    "cherry":{"price":3, "people":[]},
    "durians":{"price":4, "people":[]}
    }                                   # to store names
#TODO take in wrong user intput

def dutch(update, context):
    user_id = update._effective_chat.id
    print("goingdutch")

    # Who ordered - iterate through list of items?
    # for item in data[user_id]['item_list']:                #To comment in after testing

    if a:
        item = next(iter(a))
        price = a[item]["price"]
        print(item)
        print(price)

        bot.send_message(chat_id=update.message.chat_id,
                         text= "Who ordered " +
                                item +
                                " ?" ,
                          reply_markup = ReplyKeyboardMarkup(create_keyboard(names)),
                          #reply_markup = ForceReply(force_reply=True)
                         )
        return NAMES
    else:
        print(a)
        print(b)
        print(names)
        godutch_output(update,context)


    #TODO: Figure out how to assign multiple people to same item
def get_names(update, context):
    user_id = update._effective_chat.id
    name = update.message.text

    item = next(iter(a))
    price = a[item]["price"]

    if name == "All of the above":
        for people in names:
            b[item]["people"].append(people)
        # Do something
    else:
        if name not in names:
            names.append(name) # for keyboard
        b[item]["people"].append(name)



    print(item)
    print (price)
    print(name)
    a.pop(item)

    # add to dictionary of names if in
    # catch all option
    return dutch(update,context)



# Manually enter new name or take from dynamic keybard
# Have an all option also
# Create dictionary of people

def godutch_output(update,context):

# To do get godutch function
    results = print_dutch_results(b)
    print("end")
    bot.send_message(chat_id=update.message.chat_id,
                         text= "Here is what everyone needs to pay:\n" +
                         "`{}`".format(results),
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup = ReplyKeyboardRemove()
                         )
    return end(update,context)

def print_dutch_results(dic):
    text_width = 30                                                       #To change based on device width
    string = "Name:" + (text_width-len("Name:"))*" " + "Amount($):\n"
    my_dic = get_dutch_results(dic)

    """ To prnt the output in a formatted string form """


    for key, val in my_dic.items() :
        string += key + " "*(text_width-len(key)) + "{:.2f}".format(val) + '\n'

    # TODO: Make text_width dynamic and based on device
    # TDOD: Deal with strings that are too long - truncate them?
    return string

def get_dutch_results(dic):
    output = {}
    print(dic)
    for people in names:
        output[people] = 0
        print("hi")

    for item , value in dic.items():
        print("hello")
        print(item)
        print(value)
        price = value['price']
        people = value['people']
        no_of_people = len(people)
        payable_per_person = price / no_of_people
        print(price)
        print(people)
        print(no_of_people)
        print(payable_per_person)


        for person in people:
            output[person] += payable_per_person

    """returns a dictionary of names of people and the corressponding prices they have to pay"""
    print(output)
    return output

def create_keyboard(list_of_names):
    """create a dynamic keyboaard based on names enteed before and an all fucntion"""
    keyboard = []
    for person in list_of_names:
        button = [KeyboardButton(person)]
        keyboard.append(button)
    if keyboard:
        keyboard.append([KeyboardButton("All of the above")])   # Add this button if there is at least one entry

    return keyboard







def picture_input(update, context):

    bot.send_message(chat_id=update._effective_chat.id,
                 text="Please send a picture of your receipt",
                 ForceReply = True,
                 reply_markup=ReplyKeyboardRemove())

    return PIC


def pic_received(update,context):
    print('pic sent')
    # TODO: convo handler

        #Send message 'Processing Receipt...'
    context.bot.send_message(chat_id=update.message.chat_id,text='Processing receipt...')
        #Retrieve the id of the photo with the largest size
    photo_file = context.bot.get_file(update.message.photo[-1].file_id)
        #Save path shows which directory to save photo to - EDIT ACCORDINGLY
    save_path = '/Users/daniel/Downloads/Orbital/'  # need to change when host on heroko
        #Create path with filename of photo
    filename = os.path.join(save_path,'{}.jpg'.format(photo_file.file_id))
        #Download photo to the specified file path
    photo_file.download(filename)
        #Send message to update user that receipt has been received
    context.bot.send_message(chat_id=update.message.chat_id,text='Receipt received!')

    user_id = update._effective_chat.id
    response_dict = ocr.get_full_response_dict(filename)
    item_dict = regex.combined_parse_and_regex(response_dict,15)
    data[user_id]['item_list'] = item_dict

    pp.pprint(data[user_id])

    man_done(update,context)





def start_help():
    print("start_help")

    keyboard = [
                [KeyboardButton("Send a Photo of Receipt")],
                [KeyboardButton("Input Items Manually"), KeyboardButton("Help")],
                ]


    bot.send_message(chat_id=update._effective_chat.id,
                 text= 'Please choose either to: \n' +
                        '- Take a picture of receipt\n' +
                        #' '*5 + 'or\n' +
                        '- Key in the details manually \n\n' +
                        'Enter /start again to restart',
                 reply_markup=ReplyKeyboardMarkup(keyboard),
                 one_time_keyboard=True)

    pass








pic_or_manual = ConversationHandler(
    entry_points = [ MessageHandler(Filters.regex('^Input Items Manually$'), manual_input),
                     MessageHandler(Filters.regex('^Send a Photo of Receipt$'), picture_input),
                     MessageHandler(Filters.regex('^Help$'), start_help),
                     #MessageHandler(Filters.photo, pic_received)
                     ],

    states = {
        ITEM : [MessageHandler(Filters.text, input_item)],
        PRICE : [MessageHandler(Filters.text, input_price)],
        PIC : [MessageHandler(Filters.photo, pic_received)]
        },
    fallbacks = [CommandHandler('cancel', cancel),
                 CommandHandler('done', man_done)],
    )


split_method = ConversationHandler(
    entry_points = [ MessageHandler(Filters.regex('^GoDutch$'), dutch),
                     MessageHandler(Filters.regex('^a$'), dutch),  # To remove after testing
                    MessageHandler(Filters.regex('^Split Even$'), split)
                     ],
    states = {
        SPLITEVEN: [MessageHandler(Filters.text, get_no_of_people)],
        NAMES: [MessageHandler(Filters.text, get_names)],
        },
    fallbacks = [CommandHandler('cancel', cancel),
                 CommandHandler('end',end)],
    )




updater.dispatcher.add_handler(split_method) # To Remove after testing


















"""
def button(update, context):
    query = update.callback_query

    if query.data == 'Pic':
        query.edit_message_text("Selected option: {}\n".format(query.data) +
                                'Please send a picture of your reciept:')
        picture(update, context)

    elif query.data == 'manual':
        query.edit_message_text("Selected option: /manual"
                                )
        manual(update, context)
    elif query.data == 'Help':
        query.edit_message_text('Please choose either to: \n' +
                                '1. Take a picture of receipt\n' +
                                ' '*5 + 'or\n' +
                                '2. Key in the details manually \n\n' +
                                'Enter /start again to restart')
    else:
        context.bot.send_message(chat_id=query.message.chat_id, text="Please select a valid option")
"""


"""
def manual(update,context):

    user_id = update._effective_chat.id

    update.callback_query.edit_message_text("Please enter item number " +
                                            str(data[user_id]['item_counter']+1) +
                                            #str(int(len(data[user_id]['item_list'])+1)) +
                                            '\n' +
                                            "Items so far : \n /manual "

                                            #str(print_items(update,context))
                                            )
    #update._effective_message.edit_text('test')
    #ForceReply(force_reply=True)


"""
















### Commands
def bef_start_help(update, context):
    update.message.reply_text("Use /start to get started!")
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


### Extra Functions
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
    # Inline Mode Function
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
### Extra Functions



"""
def main():
    print(bot.getMe())
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', bef_start_help))  # Help Command






### EXTRA FUNCTIONS
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(CommandHandler('caps', caps))
    updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))
### EXTRA FUNCTIONS
    # Wrong Command
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, wrong_command)






    # Log errors
    updater.dispatcher.add_error_handler(error)
    # Start Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    # updater.idle()
to comment in later ^
if __name__ == '__main__':
    main()

# TODO: Get a keypad for number input
# TODO: Filter user inputs account for $
# TODO: To auto detect GST and service charge

"""











def main():
    print(bot.getMe())
    updater.dispatcher.add_handler(CommandHandler('start', start))
### EXTRA FUNCTIONS
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(CommandHandler('caps', caps))
    updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))
### EXTRA FUNCTIONS

    # Help Command
    #updater.dispatcher.add_handler(CommandHandler('help', help))
    # Wrong Command
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, wrong_command)

    # Log errors
    updater.dispatcher.add_error_handler(error)
    # Start Bot
   # menu.updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    # updater.idle()
    """to comment in later ^"""


    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://go-dutch-bot.herokuapp.com/" + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
