#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

number_to_train_dict = {
    1: 'purple',
    2: 'white',
    3: 'blue',
    4: 'yellow',
    5: 'orange',
    6: 'black',
    7: 'red',
    8: 'green',
    9: 'rainbow'
}


class Deck:
    def __init__(self):
        random.seed(42)

    def draw(self):
        train = number_to_train_dict[random.randint(1, 10)]
        logger.info('drew {}'.format(train))
        return train
