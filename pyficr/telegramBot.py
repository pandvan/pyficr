#!/usr/bin/env python

""" DOCS
"""

# Import statements
import sys
import logging
import pyficr
from telegram.ext import Updater, CommandHandler
from telegram import TelegramError

# Global variables
updater = None
dispatcher = None


# Functions
def start(bot, update):
    start_message = ["Hi! I'm the (Unofficial) Ficr Rally Bot.",
                     "Please type /help to get the list of commands."]

    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join(start_message))


def help_(bot, update):
    help_message = ["Following are all available bot commands:",
                    "/list - get the list of last 5 rallies",
                    "/help - show this help message"]

    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join(help_message))


def get_rank(bot, update):
    idx = int(update.message.text[1:])
    idx = idx - 1

    evnt = pyficr.get_events(limit=5)
    url = evnt[idx]["link"]

    bot.send_message(chat_id=update.message.chat_id,
                     text="Please wait a moment...")

    data = pyficr.get_rally_data(url)
    ln_str = pyficr.generate_text(data)

    # split ln_str every 4000 chars
    strs = [ln_str[i:i+4000] for i in range(0, len(ln_str), 4000)]

    try:
        for str_ in strs:
            bot.send_message(chat_id=update.message.chat_id,
                             text=str_)
    except TelegramError as e:
        print(str(e))


def list_(bot, update):
    print("inside list_ def")
    print(type(dispatcher))

    evnt = pyficr.get_events(limit=5)

    # i = 0
    # names = ["/" + enumerate(dict_['event']) for dict_ in evnt]
    names = []
    i = 0
    for dict_ in evnt:
        i = i + 1
        names.append("/{} {}".format(i, dict_["event"]))
        get_rank_handler = CommandHandler(str(i), get_rank)
        dispatcher.add_handler(get_rank_handler)

    # print("\n".join(names))

    # print(type(bot))
    # print(type(update))

    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join(names))

    print("leaving list_ def")


# Main Function
def main():
    """ DOCS
    """

    global updater
    global dispatcher

    updater = Updater(token="267428343:AAGIu0K7pm92OTrfkeLhvQhUmy8kCmdXPvM")
    dispatcher = updater.dispatcher

    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s", level=logging.DEBUG)

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler("help", help_)
    dispatcher.add_handler(help_handler)

    list_handler = CommandHandler("list", list_)
    dispatcher.add_handler(list_handler)

    updater.start_polling()

    # list_(1, 2)


# If not call as a module, run main function
if __name__ == "__main__":
    sys.exit(main())
