#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from deck import Deck
from routes import RoutesDeck


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class TicketToRide:
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.session = {'users': [], 'turn': None, 'open': True}

    def join(self, update, context):
        if self.session['open']:
            self.session['users'].append(update.message.chat_id)
            logger.info('Added {} to the game'.format(update.message.chat_id))
            update.message.reply_text('You\'ve been added to the session')
        else:
            update.message.reply_text('Sorry, the session is closed already')

    def init_game(self):
        self.deck = Deck()
        self.routes = RoutesDeck()
        self.state = [self.deck.draw() for _ in range(5)]

    def start(self, update, context):
        if not self.session['open'] or update.message.chat_id not in self.session['users']:
            update.message.reply_text('Sorry, you have to /join the open session first')
            return
        update.message.reply_text('Hi! This Ticket To Ride game is being initialized...')
        logger.info('Started new game')
        self.init_game()
        self.show_state(update, context)
        self.session['open'] = False

    def show_state(self, update, context):
        update.message.reply_text('''
            /random
            /1 {}
            /2 {}
            /3 {}
            /4 {}
            /5 {}
            '''.format(*self.state))

    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def main(self):
        """Start the bot."""
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("join", self.join))
        dispatcher.add_handler(CommandHandler("start", self.start))
        # dispatcher.add_handler(CommandHandler("random", self.random))
        # dispatcher.add_handler(CommandHandler("1", self.start))
        # dispatcher.add_handler(CommandHandler("2", self.start))
        # dispatcher.add_handler(CommandHandler("3", self.start))
        # dispatcher.add_handler(CommandHandler("4", self.start))
        # dispatcher.add_handler(CommandHandler("5", self.start))
        # dispatcher.add_handler(CommandHandler("routes", self.start))

        dispatcher.add_error_handler(self.error)

        self.updater.start_polling()

        self.updater.idle()


if __name__ == '__main__':
    with open('telegram.token') as token_file:
        token = token_file.read()
    app = TicketToRide(token)
    app.main()
