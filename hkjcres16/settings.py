# -*- coding: utf-8 -*-
import os
# Scrapy settings for hkjcres16 project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'hkjcres16'

SPIDER_MODULES = ['hkjcres16.spiders']
NEWSPIDER_MODULE = 'hkjcres16.spiders'

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'hkjcres16')
ROOT_DIR = os.path.dirname(BASE_DIR)


USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"

DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': 'vmac',
    'password': '',
    'database': 'hkresultd_oct15'
}

DOWNLOAD_DELAY = 3

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hkjcres16 (+http://www.yourdomain.com)'

FEED_EXPORTERS = {
    'csv': 'scrapy.exporters.CsvItemExporter',
}

FEED_EXPORT_FIELDS = [
    'url',
    'raceindex',
    'raceclass',
    'going',
    'courseconfig',
    'racedistance',
    'finishtime',
    'win_combo_div',
    'place_combo_div',
    'qn_combo_div',
    'qnp_combo_div',
    'tce_combo_div',
    'trio_combo_div',
    'f4_combo_div',
    'qtt_combo_div',
    'dbl9_combo_div',
    'dbl8_combo_div',
    'dbl7_combo_div',
    'dbl6_combo_div',
    'dbl5_combo_div',
    'dbl4_combo_div',
    'dbl3_combo_div',
    'dbl2_combo_div',
    'dbl1_combo_div',
    'dbl10_combo_div',
    'dbltrio1_combo_div',
    'dbltrio2_combo_div',
    'dbltrio3_combo_div',
    'tripletriocons_combo_div',
    'tripletrio_combo_div',
    'sixup_combo_div',
    'jockeychallenge_combo_div',
    'a1_div',
    'a2_div',
    'a3_div',
]
