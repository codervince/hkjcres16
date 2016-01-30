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
# MAX_TRYS = 1  # 5 by default

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hkjcres16 (+http://www.yourdomain.com)'

ITEM_PIPELINES = {
    'hkjcres16.pipelines.CsvExportPipeline': 1
}

OUTPUT_FILE_NAME = 'output_all.csv'

CSV_EXPORT_PIPELINE_FIELDS = [
    'Hkjcres16Item__url',
    'Hkjcres16Item__raceindex',
    'Hkjcres16Item__raceclass',
    'Hkjcres16Item__going',
    'Hkjcres16Item__courseconfig',
    'Hkjcres16Item__racedistance',
    'Hkjcres16Item__finishtime',
    'Hkjcres16Item__win_combo_div',
    'Hkjcres16Item__place_combo_div',
    'Hkjcres16Item__qn_combo_div',
    'Hkjcres16Item__qnp_combo_div',
    'Hkjcres16Item__tce_combo_div',
    'Hkjcres16Item__trio_combo_div',
    'Hkjcres16Item__f4_combo_div',
    'Hkjcres16Item__qtt_combo_div',
    'Hkjcres16Item__dbl9_combo_div',
    'Hkjcres16Item__dbl8_combo_div',
    'Hkjcres16Item__dbl7_combo_div',
    'Hkjcres16Item__dbl6_combo_div',
    'Hkjcres16Item__dbl5_combo_div',
    'Hkjcres16Item__dbl4_combo_div',
    'Hkjcres16Item__dbl3_combo_div',
    'Hkjcres16Item__dbl2_combo_div',
    'Hkjcres16Item__dbl1_combo_div',
    'Hkjcres16Item__dbl10_combo_div',
    'Hkjcres16Item__dbltrio1_combo_div',
    'Hkjcres16Item__dbltrio2_combo_div',
    'Hkjcres16Item__dbltrio3_combo_div',
    'Hkjcres16Item__tripletriocons_combo_div',
    'Hkjcres16Item__tripletrio_combo_div',
    'Hkjcres16Item__sixup_combo_div',
    'Hkjcres16Item__jockeychallenge_combo_div',
    'Hkjcres16Item__a1_div',
    'Hkjcres16Item__a2_div',
    'Hkjcres16Item__a3_div',

    'HorseItem__racecoursecode',
    'HorseItem__racenumber',
    'HorseItem__racedate',
    'HorseItem__horseno',
    'HorseItem__place',
    'HorseItem__finishtime',
    'HorseItem__horsecode',
    'HorseItem__runningpositions',
    'HorseItem__actualwt',
    'HorseItem__jockeycode',
    'HorseItem__trainercode',
    'HorseItem__lbw',
    'HorseItem__horsewt',
    'HorseItem__winodds',
    'HorseItem__draw',
    'HorseItem__sec_timelist',
    'HorseItem__marginsbehindleader',
]
