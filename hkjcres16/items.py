# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class JockeyItem(scrapy.Item):
    jockeycode = scrapy.Field()

class TrainerItem(scrapy.Item):
    trainercode = scrapy.Field()   

class OwnerItem(scrapy.Item):
    ownername = scrapy.Field() 


class HorseItem(scrapy.Item):
    horsecode= scrapy.Field()
    horsename= scrapy.Field()

    yob = scrapy.Field()
    samesirecodes = scrapy.Field()
    countryoforigin = scrapy.Field()
    twurl = scrapy.Field()
    veturl = scrapy.Field()
    pedigreeurl = scrapy.Field()
    importtype = scrapy.Field()
    owner = scrapy.Field()
    sirename = scrapy.Field()
    damname = scrapy.Field()
    damsirename = scrapy.Field()


class RunnerItem(scrapy.Item):
    Race_item = scrapy.Field()
    Horse_item = scrapy.Field()
    horseurl = scrapy.Field()
    chinesename = scrapy.Field()
    seasonalbrandno = scrapy.Field()
    racenumber = scrapy.Field()
    racedate = scrapy.Field()
    horsetimepermeter= scrapy.Field()
    horseprize = scrapy.Field()
    trainerprize = scrapy.Field()
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
    jtohweight= scrapy.Field()
    winodds = scrapy.Field()
    oddschance = scrapy.Field()
    winoddsrank = scrapy.Field()
    todaysrunners= scrapy.Field()
    timeperm = scrapy.Field()
    draw = scrapy.Field()
    horsereport = scrapy.Field()

    sec_timelist = scrapy.Field()
    sec1 = scrapy.Field()
    sec2= scrapy.Field()
    sec3= scrapy.Field()
    sec4= scrapy.Field()
    sec5= scrapy.Field()
    sec6= scrapy.Field()
    margin1=scrapy.Field()
    margin2=scrapy.Field()
    margin3=scrapy.Field()
    margin4=scrapy.Field()
    margin5=scrapy.Field()
    margin6=scrapy.Field()
    marginsbehindleader = scrapy.Field()
    secfinishtime = scrapy.Field()

    priority= scrapy.Field()
    todaysratingchange= scrapy.Field()
    seasonstakes= scrapy.Field()
    gear = scrapy.Field()
    l3racepoints= scrapy.Field()
    LTONewTrainer= scrapy.Field()
    GearLTOChange=scrapy.Field()
    LTODistanceChange= scrapy.Field()
    DaysSinceLastRun= scrapy.Field()
    previousruns= scrapy.Field()
    horse = scrapy.Field()
    nooftrainers = scrapy.Field()
    Starts= scrapy.Field()
    Scratched= scrapy.Field()
    CareerWins= scrapy.Field()
    Wins_d= scrapy.Field()
    Runs_d= scrapy.Field()
    WinSR_d= scrapy.Field()
    BestFinishTime_d= scrapy.Field()
    AvgWinOdds_d= scrapy.Field()

    trainer = scrapy.Field()
    jockey = scrapy.Field()

class VenueItem(scrapy.Item):
    racecoursecode = scrapy.Field()
    surface= scrapy.Field()
    isAWT= scrapy.Field()


class RaceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # day or night?
    racenumber = scrapy.Field()
    racedate = scrapy.Field()
    url = scrapy.Field()
    raceindex = scrapy.Field()
    raceclass = scrapy.Field()
    raceprize = scrapy.Field()
    going = scrapy.Field()
    venue = scrapy.Field()
    racedistance = scrapy.Field()
    finishtime = scrapy.Field()
    starterslist= scrapy.Field()
    scratchedlist = scrapy.Field()
    trainersprizes = scrapy.Field()

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
    ttraces= scrapy.Field()
    ttprize = scrapy.Field()
