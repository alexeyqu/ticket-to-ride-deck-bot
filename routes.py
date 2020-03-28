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


class RoutesDeck:
    def __init__(self):
        random.seed(42)

    def draw(self):
        return random.randint(1, 10)
