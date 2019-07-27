import modules.google_regex as regex
import modules.google_ocr as ocr
import pprint
import modules.menu as menu
from module.BOT_TOKEN import TOKEN
import os


print(menu.TOKEN)
pp = pprint.PrettyPrinter()

updater = menu.Updater(menu.TOKEN, use_context=True)
bot = menu.Bot(token = menu.TOKEN)

#def main():
    
 #   file = '/Users/seanchan/goDutch/test/testpic4.jpeg'
    
  #  response_dict = ocr.get_full_response_dict(file)
   # data = regex.combined_parse_and_regex(response_dict,15)
   # pp.pprint(data)

def main():
    print(bot.getMe())
    menu.updater.dispatcher.add_handler(menu.CommandHandler('start', menu.start))
### EXTRA FUNCTIONS
    #updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    menu.updater.dispatcher.add_handler(menu.CommandHandler('test', menu.test))
    menu.updater.dispatcher.add_handler(menu.CommandHandler('caps', menu.caps))
    menu.updater.dispatcher.add_handler(menu.InlineQueryHandler(menu.inline_caps))
### EXTRA FUNCTIONS

    # Help Command
    #updater.dispatcher.add_handler(CommandHandler('help', help))
    # Wrong Command
    #updater.dispatcher.add_handler(MessageHandler(Filters.command, wrong_command)

    # Log errors
    menu.updater.dispatcher.add_error_handler(menu.error)
    # Start Bot
    menu.updater.start_polling()
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    # updater.idle()
"""to comment in later ^"""
if __name__ == '__main__':
    main()
