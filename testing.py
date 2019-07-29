import os
import logging
import pprint
from telegram.ext import *
from telegram import *
import modules.google_regex as regex
import modules.google_ocr as ocr
#import modules.menu as menu
#from modules.BOT_TOKEN import TOKEN

### Logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
### Pretty Print
pp = pprint.PrettyPrinter(indent=4,width=20)
#pp.pprint(update.to_dict())

TOKEN = "728096945:AAEUgvz_mTe_6U17N6wTJImKDC5ei4wqfxs"
PORT = int(os.environ.get('PORT', '8443'))
updater = Updater(TOKEN, use_context=True)
bot = Bot(token = TOKEN)

print(TOKEN)

data = {}                                                                                   # Dictionary of dictionaries (user_id:item:price)
ITEM, PRICE, MANUAL, SPLITEVEN, NAMES, DUTCH, PIC, NOTHING = range(8)                       # For convo handler for manual input of items

def start(update, context):
    user_id = update._effective_chat.id
    data[user_id] = {}
    data[user_id]['prev_input'] = -1
    data[user_id]['item_list'] = {}
    data[user_id]['item_counter'] = 0                                                       # To count the number of items
    data[user_id]['go_dutch_item_list'] = {}
    data[user_id]['name_list'] =[]

    keyboard = [
                [KeyboardButton("Send a Photo of Receipt")],
                [KeyboardButton("Input Items Manually"), KeyboardButton("Help")],
                ]

    update.message.reply_text('Hello! \n''Please select an option: ',
                              reply_markup=ReplyKeyboardMarkup(keyboard),
                              one_time_keyboard=True)
    print(data)
    updater.dispatcher.add_handler(pic_or_manual)                                           # Handler to listen for manual input of items

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
    # TODO: Deal with duplicates - python dictionary cannot deal with duplicates
    # Either use spaces or blank characters or (1),(2),(3) etc...
    # TODO: Take in GST and Service Charge
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

def input_done(update,context):
    user = update.message.from_user
    logger.info("User %s done with manual/picture input.", user.first_name)

    keyboard = keyboard = [
                [KeyboardButton("GoDutch"), KeyboardButton("Split Even")],
                ]

    update.message.reply_text('Done!\n'+
                              'Do you want to GoDutch or split even ?',
                              reply_markup=ReplyKeyboardMarkup(keyboard),
                              one_time_keyboard=True
                              )
    updater.dispatcher.add_handler(split_method)
    init_dict(update, context)
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
                 reply_markup = ReplyKeyboardRemove()
                     )
    end(update,context)
    return ConversationHandler.END

def sum_all(dic):
    total = 0
    for price in dic.values():
        total += float(price['price'])
    return total

def parse_dic(dic):
    """takes in {apple:1,banana:2} -> apples":{"price":1, "people":[]},"bannna":{"price":2, "people":[]}"""
    for item, price in dic.items():
        temp = {}
        temp['price'] = price
        temp['people'] = []
        dic[item] = temp
    return dic
# TODO: Parse the dictionary to allow the item counter to be also updated
def clone_dict(a,b):
    for key, value in a.items():
        b[key] = value
        
def enumerate_names(name_list):
    output = ""
    for names in name_list:
        if names == name_list[-1]:
            output += names
            continue
        output += names + ", "
    return output


















# TODO: 
# String printing wrong 
# All of the above when pressed lags
def init_dict(update, context):
    user_id = update._effective_chat.id
    print("init dic")
    data[user_id]['item_list'] = parse_dic(data[user_id]['item_list'])              # Parse dictionary to godutch format
    clone_dict(data[user_id]['item_list'], data[user_id]['go_dutch_item_list'] )    # Clone a dummy dictionary 
    

def dutch_selected(update, context):
    user_id = update._effective_chat.id
    print("goingdutch")
    # Who ordered - iterate through list of items?    
    if data[user_id]['item_list'] != {}:
            
        print("not empty")  
        item = next(iter(data[user_id]['item_list']))                                   # Find the next item in the dictionary 
        people = data[user_id]['item_list'][item]["people"]                             # People list of that item 
        name_list = data[user_id]['name_list']                                          # List of all previously input names
        price = data[user_id]['item_list'][item]['price']                               # Price of that item

        print(data)
        print("item is")
        print(item)
        print("people sharing this item")
        print(people)
        print("price is ")
        print(price)
        print("price printed here^")

        #print(item)
        
        if bool(data[user_id]['name_list']):
            bot.send_message(chat_id=update.message.chat_id,
                         text= "Who ordered " +
                                item +
                                " ($" +
                                str(price) +
                                ") ?" ,
                          reply_markup = ReplyKeyboardMarkup(create_keyboard(people, name_list))  
                         )
            return NAMES
        else:
            bot.send_message(chat_id=update.message.chat_id,
                         text= "Who ordered " +
                                item +
                                " ($" +
                                str(price) +
                                ") ?" ,
                          reply_markup = ReplyKeyboardRemove(),   
                          #reply_markup = ForceReply(force_reply=True)
                         )
            print ("to get names")
            return NAMES
    else:
        print(data[user_id]['item_list'])
        print(data[user_id]['go_dutch_item_list'])
        print(data[user_id]['name_list'])
        godutch_output(update,context)

def pop_dict(dic):
    """To pop the items in a nested dictionary
    print("pop_dict")
    for item in dic:
        print('entered loop')
        if bool(dic):
            dic.pop(item)
            print('pop internal items')
    #return dic
"""
    print("poping_dict")
    print(dic)
    keys_to_pop = []
    for key in dic.keys():
        keys_to_pop.append(key)
        print(key)
        #del dic[key]
    print(keys_to_pop)
    for to_pop in keys_to_pop:
        #dic.pop(to_pop)
        del dic[to_pop]
        print (dic)
    print(dic)
    return dic

def get_names(update, context):
    user_id = update._effective_chat.id
    name = update.message.text
    print("in get names")
    item = next(iter(data[user_id]['item_list']))
    price = data[user_id]['item_list'][item]["price"]
    people = data[user_id]['item_list'][item]["people"]
    print(item)
    #print(data[user_id]['item_list'])
    #print(data[user_id]['go_dutch_item_list'])
    print (data)
    if name == "All of the above":
        for people in data[user_id]['name_list']:
            data[user_id]['go_dutch_item_list'][item]["people"].append(people)
            return NAMES
    elif name == 'No':
        #data[user_id]['item_list'].pop(item)   # BUG HERE
        #del data[user_id]['item_list'][item]
        #print("poping")
        #print(item)
        #pop_dict(data[user_id]['item_list'][item])
        #print (data)
        #data[user_id]['item_list'].pop(item)
        #data[user_id]['item_list'][item] = {}
        #print(data)
        data[user_id]['item_list'].pop(item)
        print(data)
        dutch_selected(update, context)
    else:
        if name not in data[user_id]['name_list']:
            data[user_id]['name_list'].append(name) # for keyboard

        data[user_id]['go_dutch_item_list'][item]["people"].append(name)

        bot.send_message(chat_id=update.message.chat_id,
                             text= "Is there anyone sharing " +
                             item +
                             " with " +
                             enumerate_names(people) +
                             " ?" ,
                             reply_markup = ReplyKeyboardMarkup(create_add_keyboard(people, data[user_id]['name_list'] )),
                             #reply_markup = ForceReply(force_reply=True)
                             )
        print(item)
        print (price)
        print(name)
    # add to dictionary of names if in
    # catch all option
        return NAMES

"""
def additional_names(update, context):
    user_id = update._effective_chat.id
    item = next(iter(data[user_id]['item_list']))
    name = update.message.text
    price = data[user_id]['item_list'][item]["price"]
    people = data[user_id]['item_list'][item]["people"]
    
    if name == "No":
        data[user_id]['item_list'].pop(item)
    
    
    else:
        a[item]["people"].append(name)
        if name not in names:
            names.append(name)
    
    return get_names(update,context)
#dutch_selected(update,context)
"""


























def godutch_output(update,context):
    user_id = update._effective_chat.id
    results = print_dutch_results(update,context,data[user_id]['go_dutch_item_list'])
    print("end")
    bot.send_message(chat_id=update.message.chat_id,
                         text= "Here is what everyone needs to pay:\n" +
                         "`{}`".format(results),
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup = ReplyKeyboardRemove()
                         )
    return end(update,context)



def get_dutch_results(update,context,dic):
    user_id = update._effective_chat.id
    output = {}
    print(dic)
    for people in data[user_id]['name_list']:
        output[people] = 0
        print("hi")

    for item , value in dic.items():
        print("hello")
        print(item)
        print(value)
        price = value['price']
        people = value['people']
        no_of_people = len(people)
        payable_per_person = float(price) / no_of_people
        print(price)
        print(people)
        print(no_of_people)
        print(payable_per_person)


        for person in people:
            output[person] += payable_per_person

    """returns a dictionary of names of people and the corressponding prices they have to pay"""
    print(output)
    return output

def print_dutch_results(update,context,dic):
    text_width = 30                                                       #To change based on device width
    string = "Name:" + (text_width-len("Name:"))*" " + "Amount($):\n"
    my_dic = get_dutch_results(update,context,dic)

    """ To print the output in a formatted string form """


    for key, val in my_dic.items() :
        string += key + " "*(text_width-len(key)) + "{:.2f}".format(val) + '\n'

    # TODO: Make text_width dynamic and based on device
    # TDOD: Deal with strings that are too long - truncate them?
    return string

def create_add_keyboard(items_list_people, name_list):
    keyboard = [["No"]]
    for person in name_list:
        if person in items_list_people:
            continue
        button = [KeyboardButton(person)]
        keyboard.append(button)
    if keyboard !=[["No"]] and len(keyboard) != 2:
        keyboard.append([KeyboardButton("All of the above")])   # Add this button if there is at least one entry and not just No
    return keyboard

def create_keyboard(items_list_people, name_list):
    """create a dynamic keyboaard based on names entered before and an all function as well as exclude names that have been already matched to the item"""
    keyboard = []
    for person in name_list:
        button = [KeyboardButton(person)]
        keyboard.append(button)
    if keyboard != [] and len(keyboard) != 1:
        print("create keybaord . list not empty")
        keyboard.append([KeyboardButton("All of the above")])   # Add this button if there is at least 2 entries
    return keyboard


def picture_input(update, context):

    bot.send_message(chat_id=update._effective_chat.id,
                     text="Please send a picture of your receipt",
                     ForceReply = True,
                     reply_markup=ReplyKeyboardRemove())
    return PIC

def pic_received(update,context):
    user_id = update._effective_chat.id
    print('pic sent')
    
    context.bot.send_message(chat_id=update.message.chat_id,text='Processing receipt...')       # Send message 'Processing Receipt...'
    photo_file = context.bot.get_file(update.message.photo[-1].file_id)                         # Retrieve the id of the photo with the largest size       BUG PRONE <------- MUST FIX !!!
    
    #save_path = '/app/test'  # need to change when host on heroko                              # Save path shows which directory to save photo to
    save_path= '/Users/daniel/Downloads/Orbital'

    filename = os.path.join(save_path,'{}.jpg'.format(photo_file.file_id))                      # Create path with filename of photo
    photo_file.download(filename)                                                               # Download photo to the specified file path    
    context.bot.send_message(chat_id=update.message.chat_id,text='Receipt received!')           # Send message to update user that receipt has been received

    
    response_dict = ocr.get_full_response_dict(filename)                                        # Running the picture through OCR
    item_dict = regex.combined_parse_and_regex(response_dict,15)                                # Running OCR output to get data to dictionary of items and prices
    data[user_id]['item_list'] = item_dict                                                      # Assigning and saving dictionary to user
    os.remove(filename)                                                                         # Deleting picture

    pp.pprint(data[user_id])

    input_done(update,context)

# TODO: Fix the bug above in this function above 



def start_help(update, context):
    keyboard = [
                [KeyboardButton("Send a Photo of Receipt")],
                [KeyboardButton("Input Items Manually"), KeyboardButton("Help")],
                ]
    bot.send_message(chat_id=update._effective_chat.id,
                 text= 'Please choose either to: \n' +
                        '- Take a picture of receipt\n' +
                        #' '*5 + 'or\n' +
                        '- Key in the details manually \n\n' +
                        'Enter /start again to restart'
                        'Enter /cancel at anytime to cancel' ,
                 reply_markup=ReplyKeyboardMarkup(keyboard),
                 one_time_keyboard=True)

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
                 CommandHandler('done', input_done)],
    )



split_method = ConversationHandler(
    entry_points = [ MessageHandler(Filters.regex('^GoDutch$'), dutch_selected),
                    MessageHandler(Filters.regex('^Split Even$'), split)
                     ],
    states = {
        SPLITEVEN: [MessageHandler(Filters.text, get_no_of_people)],
        NAMES: [MessageHandler(Filters.text, get_names)],
        
       #NOTHING : [MessageHandler(Filters.text, dutch_selected)],
        },
    fallbacks = [CommandHandler('cancel', cancel),
                 CommandHandler('end',end)],
    )

# TODO: Combine all states for each handler into one converstion handler and only one entry point - /start

# TODO: Make sure convo handler ends


#update._effective_message.edit_text('test')
#ForceReply(force_reply=True)

### Commands
def bef_start_help(update, context):
    update.message.reply_text("Use /start to get started!")
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

"""
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
    """    
### EXTRA FUNCTIONS
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    #updater.dispatcher.add_handler(CommandHandler('test', test))   
    #updater.dispatcher.add_handler(CommandHandler('caps', caps))
    #updater.dispatcher.add_handler(InlineQueryHandler(inline_caps))
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, wrong_command)
    """
    # Log errors
    updater.dispatcher.add_error_handler(error)
    # Start Bot
    updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    # updater.idle()

"""
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://go-dutch-bot.herokuapp.com/" + TOKEN)
    updater.idle()

"""
if __name__ == '__main__':
    main()


# TODO: Get a keypad for number input
# TODO: Filter user inputs account for $
# TODO: To auto detect GST and service charge
# TODO take in wrong user intput
