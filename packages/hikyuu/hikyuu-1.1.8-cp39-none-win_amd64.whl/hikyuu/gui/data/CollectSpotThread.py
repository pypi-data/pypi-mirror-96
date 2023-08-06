#!/usr/bin/python
# -*- coding: utf8 -*-
# cp936

import logging
import time
import datetime
from math import ceil
from PyQt5.QtCore import QThread, QWaitCondition, QMutex

from hikyuu import Datetime, TimeDelta, hikyuu_init, StockManager, constant
from hikyuu.util import *
from hikyuu.fetcher.stock.zh_stock_a_sina_qq import get_spot, get_spot_parallel
from hikyuu.gui.spot_server import collect


class CollectSpotThread(QThread):
    def __init__(self, config, hku_config_file):
        super(self.__class__, self).__init__()
        self.working = True
        self._config = config
        self.hku_config_file = hku_config_file
        self._interval = config.getint('collect', 'interval', fallback=60 * 60)
        self._phase1_start_time = config.get('collect', 'phase1_start', fallback='09:00')
        self._phase1_end_time = config.get('collect', 'phase1_end', fallback='12:05')
        self._phase2_start_time = config.get('collect', 'phase2_start', fallback='13:00')
        self._phase2_end_time = config.get('collect', 'phase2_end', fallback='15:05')
        self._use_zhima_proxy = config.getboolean('collect', 'use_zhima_proxy', fallback=False)
        self._source = config.get('collect', 'source', fallback='sina')

    def __del__(self):
        hku_info("Quit CollectSpotThread")

    @hku_catch()
    def run(self):
        collect(
            self._use_zhima_proxy, self._source, self._interval,
            '{}-{}'.format(self._phase1_start_time, self._phase1_end_time),
            '{}-{}'.format(self._phase2_start_time, self._phase2_end_time), True
        )


class_logger(CollectSpotThread)