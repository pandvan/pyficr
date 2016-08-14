#!/usr/bin/env python

""" DOCS
"""

import sys
import logging
import pyficr
from telegram.ext import Updater, CommandHandler


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Hi! I'm the pyFicr Telegram Bot")


def list_(bot, update):
    evnt = pyficr.get_events(limit=5)
    print("\n\n===\n\n")

    result = ""
    names = ["<a href='#xxx'>" + dict_['event'] + "</a>" for dict_ in evnt]


        #print(dict_['event'])
        #result = result + " " + dict_['event']
        #dict_['link']

        # for k, v in dict_.items():
            # print("key: {}, value: {}".format(k, v))
            # if(k=="event")
            # result +

    #print(result)
    bot.send_message(chat_id=update.message.chat_id,
                     text="\n".join(names))


def main():
    """ DOCS
    """

    updater = Updater(token="256440402:AAFCJIa_E6vaW7cYsq_46ttOeNk9htAW4BU")
    dispatcher = updater.dispatcher

    # logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - "
    #                           "%(message)s", level=logging.DEBUG)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    list_handler = CommandHandler('list', list_)
    dispatcher.add_handler(list_handler)

    updater.start_polling()

    #list_()


if __name__ == '__main__':
    sys.exit(main())
