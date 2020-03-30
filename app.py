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


COLORS = {
    'purple': '🟪',
    'white': '  ',
    'blue': '🟦',
    'yellow': '🟨',
    'orange': '🟧',
    'black': '⬛',
    'red': '🟥',
    'green': '🟩',
    'rainbow': '🏳️‍🌈'
}


def train_to_color(train):
    return COLORS[train]


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

    def send_to_all(self, message, context):
        for user in self.session['users']:
            context.bot.send_message(chat_id=user, text=message)

    def start(self, update, context):
        if not self.session['open'] or update.message.chat_id not in self.session['users']:
            update.message.reply_text('Sorry, you have to /join the open session first')
            return
        self.send_to_all('Hi! This Ticket To Ride game is being initialized...', context)
        logger.info('Started new game')
        self.init_game()
        self.send_to_all(self.get_state_string(), context)
        self.session['open'] = False

    def get_state_string(self):
        return '''
            /random \n /1 {} \n /2 {} \n /3 {} \n /4 {} \n /5 {}
        '''.format(*map(train_to_color, self.state))

    def card_random(self, update, context):
        train = self.deck.draw()
        for user in self.session['users']:
            if user == update.message.chat_id:
                update.message.reply_text('You drew {}'.format(train))
            else:
                context.bot.send_message(chat_id=user, text='Random card was drawn')   
        self.send_to_all(self.get_state_string(), context)

    def card_1(self, update, context):
        update.message.reply_text('You drew {}'.format(self.state[0]))
        self.state[0] = self.deck.draw()
        self.send_to_all(self.get_state_string(), context)

    def card_2(self, update, context):
        update.message.reply_text('You drew {}'.format(self.state[1]))
        self.state[1] = self.deck.draw()
        self.send_to_all(self.get_state_string(), context)

    def card_3(self, update, context):
        update.message.reply_text('You drew {}'.format(self.state[2]))
        self.state[2] = self.deck.draw()
        self.send_to_all(self.get_state_string(), context)

    def card_4(self, update, context):
        update.message.reply_text('You drew {}'.format(self.state[3]))
        self.state[3] = self.deck.draw()
        self.send_to_all(self.get_state_string(), context)

    def card_5(self, update, context):
        update.message.reply_text('You drew {}'.format(self.state[4]))
        self.state[4] = self.deck.draw()
        self.send_to_all(self.get_state_string(), context)

    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def palette(self, update, context):
        update.message.reply_text('\n'.join(['{} {}'.format(color, symbol) for color, symbol in COLORS.items()]))


    def main(self):
        """Start the bot."""
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("join", self.join))
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("random", self.card_random))
        dispatcher.add_handler(CommandHandler("1", self.card_1))
        dispatcher.add_handler(CommandHandler("2", self.card_2))
        dispatcher.add_handler(CommandHandler("3", self.card_3))
        dispatcher.add_handler(CommandHandler("4", self.card_4))
        dispatcher.add_handler(CommandHandler("5", self.card_5))
        dispatcher.add_handler(CommandHandler("palette", self.palette))
        # dispatcher.add_handler(CommandHandler("routes", self.start))

        dispatcher.add_error_handler(self.error)

        self.updater.start_polling()

        self.updater.idle()


if __name__ == '__main__':
    with open('telegram.token') as token_file:
        token = token_file.read()
    app = TicketToRide(token)
    app.main()
 