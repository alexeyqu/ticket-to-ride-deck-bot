#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

COLORS_text = ['purple', 'white', 'blue', 'yellow', 'orange', 'black', 'red', 'green', 'rainbow']
COLORS_icon = ['🟪', '  ', '🟦', '🟨', '🟧', '⬛', '🟥', '🟩',  '🏳️‍🌈']
COLORS_text_to_icon = {text : icon for text, icon in zip(COLORS_text, COLORS_icon)}

class Deck:
    #DECK_initial_configuration = {color : 1 for color in COLORS_text}
    DECK_initial_configuration = dict([(color, 12 if color is not 'rainbow' else 14) for color in COLORS_text])

    def __init__(self):
        random.seed(42)
        self.configuration = self.DECK_initial_configuration.copy()

    def draw(self):
        allowed_colors = [color for color in COLORS_text if self.configuration[color] > 0]

        if not allowed_colors:
            self.configuration = self.DECK_initial_configuration.copy()
            allowed_colors = COLORS_text
            logger.info('Deck has been restarted.')

        train = random.choice(allowed_colors)
        self.configuration[train] -= 1
        logger.info('drew {}'.format(train))
        logger.info('configuration: %s', self.configuration)
        return train

class RoutesDeck:
    SHORT_ROUTES = [
        "Athina-Angora (5)",
        "Budapest-Sofia (5)",
        "Frankfurt-Kobenhavn (5)",
        "Rostov-Erzurum (5)",
        "Sofia-Smyrna (5)",
        "Kyiv-Petrograd (6)",
        "Zurich-Brindisi (6)",
        "Zurich-Budapest (6)",
        "Warszawa-Smolensk (6)",
        "Zagrab-Brindisi (6)",
        "Paris-Zagreb (7)",
        "Brest-Marseille (7)",
        "London-Berlin (7)",
        "Edinburgh-Paris (7)",
        "Amsterdam-Pamplona (7)",
        "Roma-Smyrna (8)",
        "Palermo-Constantinople (8)",
        "Sarajevo-Sevastopol (8)",
        "Madrid-Dieppe (8)",
        "Barcelona-Bruxelles (8)",
        "Paris-Wien (8)",
        "Barcelona-Munchen (8)",
        "Brest-Venezia (8)",
        "Smolensk-Rostov (8)",
        "Marseille-Essen (8)",
        "Kyiv-Sochi (8)",
        "Madrid-Zurich (8)",
        "Berlin-Bucuresti (8)",
        "Bruxelles-Danzic (9)",
        "Berlin-Roma (9)",
        "Angora-Kharkov (10)",
        "Riga-Bucuresti (10)",
        "Essen-Kyiv (10)",
        "Venizia-Constantinople (10)",
        "London-Wien (10)",
        "Athina-Wilno (11)",
        "Stockholm-Wien (11)",
        "Berlin-Moskva (12)",
        "Amsterdam-Wilno (12)",
        "Frankfurt-Smolensk (13)",
    ]

    LONG_ROUTES = [
        "Lisboa-Danzic (20)",
        "Brest-Petrograd (20)",
        "Palermo-Moskva (20)",
        "Kobenhavn-Erzurum (21)",
        "Edinburgh-Athina (21)",
        "Cadiz-Stockholm (21)",
    ]

    def __init__(self):
        random.seed(42)
        self.configuration_short_routes = self.SHORT_ROUTES.copy()
        self.configuration_long_routes = self.LONG_ROUTES.copy()

    def draw_short_route(self):
        route = None
        if self.configuration_short_routes:
            route = random.choice(self.configuration_short_routes)
            self.configuration_short_routes.remove(route)
            logger.info("drew {} from SHORT_ROUTES".format(route))
            logger.info("configuration_short_routes: %s", self.configuration_short_routes)
        else:
            logger.info("SHORT_ROUTES deck is empty.")
        
        return route

    def draw_long_route(self):
        route = None
        if self.configuration_long_routes:
            route = random.choice(self.configuration_long_routes)
            self.configuration_long_routes.remove(route)
            logger.info("drew {} from LONG_ROUTES".format(route))
            logger.info("configuration_long_routes: %s", self.configuration_long_routes)
        else:
            logger.info("LONG_ROUTES deck is empty.")

        return route

class TicketToRide:
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.session = {'users': [], 'turn': None, 'open': True}
        self._COLORS_TYPE = 'text'

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

    def send_photo_to_all(self, photo, context):
        for user in self.session['users']:
            context.bot.send_photo(chat_id=user, photo=photo)

    def start(self, update, context):
        if not self.session['open'] or update.message.chat_id not in self.session['users']:
            update.message.reply_text('Sorry, you have to /join the open session first')
            return
        self.send_to_all('Hi! This Ticket To Ride game is being initialized...', context)
        logger.info('Started new game')
        self.init_game()
        self.send_to_all(self.get_state_string(), context)

        #state_photos = self.get_state_photos()
        #for photo in state_photos:
        #    msg = self.send_photo_to_all(photo, context)
        #self.session['open'] = False

    def train_to_color(self, train):
        if self._COLORS_TYPE == 'text':
            return train
        elif self._COLORS_TYPE == 'icon':
            return COLORS_text_to_icon[train]

    def get_state_string(self):
        return '''
            /random \n /1 {} \n /2 {} \n /3 {} \n /4 {} \n /5 {}
        '''.format(*map(self.train_to_color, self.state))

    #def get_state_photos(self):
    #    return [open(train_to_color(train), 'rb') for train in self.state]

    def card_random(self, update, context):
        train = self.deck.draw()
        for user in self.session['users']:
            if user == update.message.chat_id:
                update.message.reply_text('You drew {}'.format(train))
            else:
                context.bot.send_message(chat_id=user, text='Random card was drawn')   
        self.send_to_all(self.get_state_string(), context)

    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)
    
    def select_card(self, card_number, update, context):
        update.message.reply_text('You drew {}'.format(self.state[card_number]))
        self.state[card_number] = self.deck.draw()
        self.send_to_all(self.get_state_string(), context)

    def text_colors(self, update, context):
        self._COLORS_TYPE = 'text'
        update.message.reply_text(self.get_state_string())
    
    def icon_colors(self, update, context):
        self._COLORS_TYPE = 'icon'
        update.message.reply_text(self.get_state_string())

    def draw_short_route(self, update, context):
        route = self.routes.draw_short_route()
        if route is not None:
            update.message.reply_text('You drew {}'.format(route))
        else:
            update.message.reply_text('SHORT_ROUTE deck is empty.')

    def draw_long_route(self, update, context):
        route = self.routes.draw_long_route()
        if route is not None:
            update.message.reply_text('You drew {}'.format(route))
        else:
            update.message.reply_text('LONG_ROUTE deck is empty.')

    def main(self):
        """Start the bot."""
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("join", self.join))
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("random", self.card_random))
        dispatcher.add_handler(CommandHandler("1", lambda update, context: self.select_card(0, update, context)))
        dispatcher.add_handler(CommandHandler("2", lambda update, context: self.select_card(1, update, context)))
        dispatcher.add_handler(CommandHandler("3", lambda update, context: self.select_card(2, update, context)))
        dispatcher.add_handler(CommandHandler("4", lambda update, context: self.select_card(3, update, context)))
        dispatcher.add_handler(CommandHandler("5", lambda update, context: self.select_card(4, update, context)))
        dispatcher.add_handler(CommandHandler("text_colors", self.text_colors))
        dispatcher.add_handler(CommandHandler("icon_colors", self.icon_colors))
        dispatcher.add_handler(CommandHandler("short_route", self.draw_short_route))
        dispatcher.add_handler(CommandHandler("long_route", self.draw_long_route))
        #dispatcher.add_handler(CommandHandler("help", self.help))

        dispatcher.add_error_handler(self.error)

        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    with open('telegram.token') as token_file:
        token = token_file.read().rstrip()
        print(token)
    app = TicketToRide(token)
    app.main()