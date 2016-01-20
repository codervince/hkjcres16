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

DOWNLOAD_DELAY=3

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hkjcres16 (+http://www.yourdomain.com)'
