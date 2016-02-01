# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HorseItem(scrapy.Item):
    hkjcres16_item = scrapy.Field()

    racecoursecode = scrapy.Field()
    racenumber = scrapy.Field()
    racedate = scrapy.Field()
    horseno = scrapy.Field()
    place = scrapy.Field()
    finishtime = scrapy.Field()
    horsecode = scrapy.Field()
    runningpositions = scrapy.Field()
    actualwt = scrapy.Field()
    jockeycode = scrapy.Field()
    trainercode = scrapy.Field()
    lbw = scrapy.Field()
    horsewt = scrapy.Field()
    winodds = scrapy.Field()
    winoddsrank = scrapy.Field()
    todaysrunners= scrapy.Field()
    timeperm = scrapy.Field()
    draw = scrapy.Field()
    horsereport = scrapy.Field()

    sec_timelist = scrapy.Field()
    marginsbehindleader = scrapy.Field()
    secfinishtime = scrapy.Field()


class Hkjcres16Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    raceindex = scrapy.Field()
    raceclass = scrapy.Field()
    going = scrapy.Field()
    courseconfig = scrapy.Field()
    racedistance = scrapy.Field()
    finishtime = scrapy.Field()
    win_combo_div = scrapy.Field()
    place_combo_div = scrapy.Field()
    qn_combo_div = scrapy.Field()
    qnp_combo_div = scrapy.Field()
    tce_combo_div = scrapy.Field()
    trio_combo_div = scrapy.Field()
    f4_combo_div = scrapy.Field()
    qtt_combo_div = scrapy.Field()
    dbl9_combo_div = scrapy.Field()
    dbl8_combo_div = scrapy.Field()
    dbl7_combo_div = scrapy.Field()
    dbl6_combo_div = scrapy.Field()
    dbl5_combo_div = scrapy.Field()
    dbl4_combo_div = scrapy.Field()
    dbl3_combo_div = scrapy.Field()
    dbl2_combo_div = scrapy.Field()
    dbl1_combo_div = scrapy.Field()
    dbl10_combo_div = scrapy.Field()
    dbltrio1_combo_div = scrapy.Field()
    dbltrio2_combo_div = scrapy.Field()
    dbltrio3_combo_div = scrapy.Field()
    tripletriocons_combo_div = scrapy.Field()
    tripletrio_combo_div = scrapy.Field()
    sixup_combo_div = scrapy.Field()
    jockeychallenge_combo_div = scrapy.Field()
    a1_div = scrapy.Field()
    a2_div = scrapy.Field()
    a3_div = scrapy.Field()
    sectional_time_url = scrapy.Field()
