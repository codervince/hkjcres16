import scrapy
from scrapy.loader import ItemLoader
from hkjcres16.items import Hkjcres16Item, HorseItem
from scrapy.loader.processors import TakeFirst,Compose, MapCompose, Identity, Join
from urlparse import urlparse
from collections import defaultdict,OrderedDict, Counter
#from selenium import webdriver
#from time import sleep
import urllib
import re
import logging
import csv
from datetime import datetime
import itertools
from hkjcres16.utilities import *


class DefaultListOrderedDict(OrderedDict):
    def __missing__(self,k):
        self[k] = []
        return self[k]

def divprocessor(divlist):
    return divprocessor

def timetofloat(t):
    return float("{0:.2f}".format(float(t)))

def dorunningpositions(l):
    return "-".join(l)

class HorseItemLoader(ItemLoader):
    #default_output_processor = TakeFirst()
    # place_out = Join()
    # actualwt_out = Join()
    
    #runningpositions_out = Compose(dorunningpositions)
     pass

class RaceItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    raceindex_in = MapCompose(int)
    racedistance_in = Compose(lambda v: v[0], int)
    finishtime_in = MapCompose(timetofloat)
    finishtime_out = TakeFirst()
    f4_combo_div_out = Join()
    win_combo_div_out = Join()
    place_combo_div_out = Join()
    qn_combo_div_out = Join()
    qnp_combo_div_out = Join()
    tce_combo_div_out = Join()
    trio_combo_div_out = Join()
    f4_combo_div_out = Join()
    qtt_combo_div_out = Join()
    dbl9_combo_div_out = Join()
    dbl8_combo_div_out = Join()
    dbl7_combo_div_out = Join()
    dbl6_combo_div_out = Join()
    dbl5_combo_div_out = Join()
    dbl4_combo_div_out = Join()
    dbl3_combo_div_out = Join()
    dbl2_combo_div_out = Join()
    dbl1_combo_div_out = Join()
    dbl10_combo_div_out = Join()
    dbltrio1_combo_div_out = Join()
    dbltrio2_combo_div_out = Join()
    dbltrio3_combo_div_out = Join()
    tripletriocons_combo_div_out= Join()
    tripletrio_combo_div_out= Join()
    sixup_combo_div_out = Join()
    jockeychallenge_combo_div_out = Join()
    compositewin_div_out = Join()

logger = logging.getLogger('hkjcres_application')

class HkjcresSpider(scrapy.Spider):
    name = "hkjcres"
    allowed_domains = ["racing.hkjc.com"]


    def __init__(self, input_filename='input.csv', *args, **kwargs):
        super(HkjcresSpider, self).__init__(*args, **kwargs)

        with open(input_filename, 'r') as f:
            self.input_data = list(csv.DictReader(f, skipinitialspace=True))

        self.base_url = "http://racing.hkjc.com/racing/Info/Meeting/Results/English/Local/"

    def start_requests(self):
        for data in self.input_data:
            url = self.base_url + data['racedate'] + '/' + data['racecoursecode'] + '/'

            self.noraces = int(data['noraces'])
            self.racedate = datetime.strptime(data['racedate'], '%Y%M%d')
            self.racecoursecode = data['racecoursecode'] 


            for i in range(1, self.noraces + 1):
                yield scrapy.Request(url + '{0:01}'.format(i), self.parse, meta={'try_num': 1, 
                    'racedate': datetime.strftime(self.racedate, '%Y%m%d'), 
          
                'racecoursecode': self.racecoursecode })

    def parse(self, response):
        logger.info('A response from %s just arrived!', response.url)
        loader = RaceItemLoader(Hkjcres16Item(), response=response)
        item = Hkjcres16Item()

        if int(response.url.split('/')[-1]) > 9:
            todaysracenumber = '{}'.format(response.url.split('/')[-1])
        else:
            todaysracenumber = '{}'.format(response.url.split('/')[-1])
        #basic race information

        # item['url'] = response.url
        loader.add_value('url', response.url)

        raceindex_path = re.compile(r'\((\d+)\)')
        item['raceindex'] = response.selector.xpath('//div[@class="boldFont14 color_white trBgBlue"]//text()').re(r'\((\d+)\)')
        loader.add_value('raceindex', response.selector.xpath('//div[@class="boldFont14 color_white trBgBlue"]//text()').re(r'\((\d+)\)'))

        #race details table
        newraceinfo = response.xpath('//table[@class ="tableBorder0 font13"]//*[self::td or self::td/span]//text()').extract()

        try:
            raceclass = newraceinfo[0].replace('-', '').strip()
        except IndexError:
            try_num = response.meta['try_num']
            if try_num >= self.settings.get('MAX_TRYS', 5):
                logger.info('Failed! Has reached the maximum number of attempts. %s', response.url)
                raise StopIteration

            logger.info('Add again to query %s', response.url)
            yield scrapy.Request(response.url, self.parse, dont_filter=True, meta={'try_num': try_num + 1})
            raise StopIteration

        going = response.xpath('//table[@class ="tableBorder0 font13"]//td[contains(text(),"Going")]/following-sibling::*/text()').extract()[0]
        racesurface = response.xpath('//table[@class ="tableBorder0 font13"]//td[contains(text(),"Course")]/following-sibling::*/text()').extract()[0]
        racedistance = newraceinfo[1].split(u'-')[0].replace(u'm', u'').replace(u'M', u'').strip()
        newsectionaltimes = response.xpath('//table[@class ="tableBorder0 font13"]//td[text()="Sectional Time :"]/following-sibling::td/text()').extract()
        winningsecs = map(float, newsectionaltimes)
        finishtime = sum(winningsecs)
        loader.add_value('raceclass', raceclass)
        loader.add_value('courseconfig', racesurface)
        loader.add_value('racedistance', racedistance)
        loader.add_value('finishtime', finishtime)
        loader.add_value('going', going)

        #DIVIDEND TABLE
        markets = [ 'WIN', 'PLACE', 'QUINELLA', 'QUINELLA PLACE', 'TIERCE', 'TRIO', 'FIRST 4', 'QUARTET','9TH DOUBLE', 'TREBLE',
            '3RD DOUBLE TRIO' , 'SIX UP', 'JOCKEY CHALLENGE',
            '8TH DOUBLE', '8TH DOUBLE', '2ND DOUBLE TRIO', '6TH DOUBLE', 'TRIPLE TRIO(Consolation)',
            'TRIPLE TRIO', '5TH DOUBLE',
            '5TH DOUBLE', '1ST DOUBLE TRIO', '3RD DOUBLE' ,
            '2ND DOUBLE', '1ST DOUBLE']
        markets2 = ['A1', 'A2', 'A3']

        isdividend = response.xpath("//td[text() ='Dividend']/text()").extract()

        div_info = defaultdict(list)
        if isdividend:
            for m in markets:
                try:
                    xpathstr = str("//tr[td/text() = 'Dividend']/following-sibling::tr[td/text()=")
                    xpathstr2 = str("]/td/text()")
                    win_divs =response.xpath(xpathstr + "'" + str(m) + "'" + xpathstr2).extract()
                    div_info[win_divs[0]] = [ win_divs[1],win_divs[2] ]
                    # print response.meta['racenumber']
                except:
                    div_info[m] = None
        #post race date = ?
        div_info['JOCKEY CHALLENGE'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='JOCKEY CHALLENGE']/following-sibling::td/text()").extract()
        compwinstartdate = datetime.strptime("20151025", '%Y%M%d')
        div_info['A1'] = None
        div_info['A2'] = None
        div_info['A3'] = None
        todaysracedate = datetime.strptime('{}'.format(response.url.split('/')[-3]), '%Y%M%d')
        todaysracedate_str =  datetime.strftime(todaysracedate, "%Y%m%d")
        todaysracecoursecode = response.url.split('/')[-2]
        if todaysracedate >= compwinstartdate:
            div_info['A1'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A1']/following-sibling::td/text()").extract()
            div_info['A2'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A2']/following-sibling::td/text()").extract()
            div_info['A3'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A3']/following-sibling::td/text()").extract()
        #parse our TT DIV INFO and other PRIZES
        # 'tripletrio_combo_div': u'1,2>5,10/2,6,10/1,4,8 3,826,375.00'
        ttdiv = None
        ttconsdiv = None
        if div_info['TRIPLE TRIO']:
            ttdiv_ = div_info['TRIPLE TRIO'][0].split(" ")[-1]
            ttdiv= float(ttdiv_.replace(',',''))
        if div_info['TRIPLE TRIO(Consolation)']:
            ttconsdiv_ = div_info['TRIPLE TRIO(Consolation)'][0].split(" ")[-1]
            ttconsdiv= float(ttdiv_.replace(',',''))
        #sectional urls
        # what happens if cant get sectional URL? Item loader will return null
        loader.add_value('sectional_time_url', response.xpath('//div[@class="rowDiv15"]/div[@class="rowDivRight"]/a/@href').extract())
        # loader.add_value('runnercodes', response.xpath('//table[@class="tableBorder trBgBlue tdAlignC number12 draggable"]//td[@class="tdAlignL font13 fontStyle"][1]/text()').extract())


        #GRAY = EVEN

        horsecode_pat = re.compile(r"horseno=(?P<str>.+)")

        #or collect entire lists

        logger.info(div_info)

        loader.add_value('win_combo_div', div_info['WIN'])
        loader.add_value('place_combo_div', div_info['PLACE'])
        loader.add_value('qn_combo_div' , div_info['QUINELLA'])
        loader.add_value('qnp_combo_div' , div_info['QUINELLA PLACE'])
        loader.add_value('tce_combo_div' , div_info['TIERCE'])
        loader.add_value('trio_combo_div' , div_info['TRIO'])
        loader.add_value('f4_combo_div' , div_info['FIRST 4'])
        loader.add_value('qtt_combo_div' , div_info['QUARTET'])
        loader.add_value('dbl9_combo_div' , div_info['9TH DOUBLE'])
        loader.add_value('dbl8_combo_div' , div_info['8TH DOUBLE'])
        loader.add_value('dbl7_combo_div' , div_info['7TH DOUBLE'])
        loader.add_value('dbl6_combo_div' , div_info['6TH DOUBLE'])
        loader.add_value('dbl5_combo_div' , div_info['5TH DOUBLE'])
        loader.add_value('dbl4_combo_div' , div_info['4TH DOUBLE'])
        loader.add_value('dbl3_combo_div' , div_info['3RD DOUBLE'])
        loader.add_value('dbl2_combo_div' , div_info['2ND DOUBLE'])
        loader.add_value('dbl1_combo_div' , div_info['1ST DOUBLE'])
        loader.add_value('dbl10_combo_div' , div_info['10TH DOUBLE'])
        loader.add_value('dbltrio1_combo_div' , div_info['1ST DOUBLE TRIO'])
        loader.add_value('dbltrio2_combo_div' , div_info['2ND DOUBLE TRIO'])
        loader.add_value('dbltrio3_combo_div' , div_info['3RD DOUBLE TRIO'])
        loader.add_value('tripletriocons_combo_div' , div_info['TRIPLE TRIO(Consolation)'])
        loader.add_value('tripletrio_combo_div', div_info['TRIPLE TRIO'])
        loader.add_value('a1_div', div_info['A1'])
        loader.add_value('a2_div', div_info['A2'])
        loader.add_value('a3_div', div_info['A3'])
        loader.add_value('sixup_combo_div', div_info['SIX UP'])
        loader.add_value('jockeychallenge_combo_div', div_info['JOCKEY CHALLENGE'])
        

        # sectional_time_url_ = response.xpath('//div[@class="rowDiv15"]/div[@class="rowDivRight"]/a[@href]').extract()
        # for sel in response.xpath('//ul/li'):
        #
        #     loader.add_xpath('title', 'a/text()')
        #     loader.add_xpath('link', 'a/@href')
        #     loader.add_xpath('desc', 'text()')
        # return item

        hkjcres16_item = loader.load_item()

        horse_items = []

        ## winodds, lbw, finishtime
        agg_winodds = OrderedDict()

        horsecode_pat = re.compile(r"horseno=(?P<str>.+)")
        for i,row in enumerate(response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgGrey']")):
            horseloader = HorseItemLoader(HorseItem())
            horseloader.add_value('hkjcres16_item', hkjcres16_item)
            horsecode = horsecode_pat.findall(row.xpath('./td[3]/a/@href').extract()[0]) or None
            horsename = row.xpath('./td[3]/a/text()').extract()[0]
            place = row.xpath('./td[1]/text()').extract()[0]
            _horseno= row.xpath("./td[2]/text()").extract()
            horseno = _horseno[0] if _horseno else 99
            actualwt = row.xpath('./td[6]//text()').extract()[0]
            horsewt = row.xpath('./td[7]//text()').extract()[0]
            draw = row.xpath('./td[8]//text()').extract()[0]
            lbw = horselengthprocessor(row.xpath('./td[9]//text()').extract()[0])
            winodds = getodds(row.xpath('./td[12]/text()').extract()[0])
            if type(horsecode)== type([]):
                horsecode = horsecode[0]
            agg_winodds[horsecode] = winodds
            finishtime = get_sec(row.xpath('./td[11]/text()').extract()[0])
            runningpositions = ">".join(row.xpath('./td[10]/table//td//text()').extract())

            _jockeycode = row.xpath('./td[4]/a/@href').extract()
            _trainercode = row.xpath('./td[5]/a/@href').extract()
            if _jockeycode:
                jockeycode = _jockeycode[0]
                jockeycode = re.match(r'^http://www.hkjc.com/english/racing/jockeyprofile.asp?.*jockeycode=(?P<str>[^&]*)(&.*$|$)', jockeycode).groupdict()['str']
            else:
                jockeycode = None
            if _trainercode:
                trainercode = _trainercode[0]
                trainercode = re.match(r'^http://www.hkjc.com/english/racing/trainerprofile.asp?.*trainercode=(?P<str>[^&]*)(&.*$|$)', trainercode).groupdict()['str']
            else:
                trainercode = None
            #Identity
            horseloader.add_value('racedate', todaysracedate_str)
            horseloader.add_value('racecoursecode', todaysracecoursecode)
            horseloader.add_value('racenumber', todaysracenumber)
            ###horse specific
            horseloader.add_value('horseno', horseno)
            horseloader.add_value('horsecode', horsecode)
            horseloader.add_value('jockeycode', jockeycode)
            horseloader.add_value('trainercode', trainercode)
            horseloader.add_value('place', place)
            horseloader.add_value('finishtime', str(finishtime))
            horseloader.add_value('actualwt', actualwt)
            horseloader.add_value('runningpositions', runningpositions)
            horseloader.add_value('lbw', str(lbw))
            horseloader.add_value('draw', draw)
            horseloader.add_value('winodds', str(winodds))
            horseloader.add_value('horsewt', horsewt)

            logger.info("todaysracedate loop %s" % todaysracedate_str)
            logger.info("todaysracecoursecode loop %s" % todaysracecoursecode)
            logger.info("todaysracenumber loop %s" % todaysracenumber)
            logger.info("place loop %s" % place)
            logger.info("horseno loop %s" % horseno)
            logger.info("horsecode loop %s" % horsecode)
            logger.info("jockeycode loop %s" % jockeycode)
            logger.info("trainercode loop %s" % trainercode)
            logger.info("draw loop %s" % draw)
            logger.info("lbw loop %s" % lbw)
            logger.info("runningpositions loop %s" % runningpositions)
            logger.info("actualwt loop %s" % actualwt)
            logger.info("horse wt loop %s" % horsewt)
            logger.info("finishtimeloop %s" % finishtime)
            logger.info("winodds loop %s" % winodds)
            logger.info("ttdiv consdiv loop %s- %s" % (ttdiv, ttconsdiv))

            horse_items += [horseloader.load_item()]


        for row in response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgWhite']"):
            horseloader = HorseItemLoader(HorseItem())
            horseloader.add_value('hkjcres16_item', hkjcres16_item)

            horsecode = horsecode_pat.findall(row.xpath('./td[3]/a/@href').extract()[0]) or None
            horsename = row.xpath('./td[3]/a/text()').extract()[0]
            place = row.xpath('./td[1]/text()').extract()[0]
            horseno= row.xpath("./td[2]/text()").extract()
            _horseno= row.xpath("./td[2]/text()").extract()
            horseno = _horseno[0] if _horseno else 99
            actualwt = row.xpath('./td[6]//text()').extract()[0]
            horsewt = row.xpath('./td[7]//text()').extract()[0]
            draw = row.xpath('./td[8]//text()').extract()[0]
            lbw = horselengthprocessor(row.xpath('./td[9]//text()').extract()[0])
            winodds = getodds(row.xpath('./td[12]/text()').extract()[0])
            if type(horsecode)== type([]):
                horsecode = horsecode[0]
            agg_winodds[horsecode] = winodds
            finishtime = get_sec(row.xpath('./td[11]/text()').extract()[0])
            runningpositions = ">".join(row.xpath('./td[10]/table//td//text()').extract())

            _jockeycode = row.xpath('./td[4]/a/@href').extract()
            _trainercode = row.xpath('./td[5]/a/@href').extract()
            if _jockeycode:
                jockeycode = _jockeycode[0]
                jockeycode = re.match(r'^http://www.hkjc.com/english/racing/jockeyprofile.asp?.*jockeycode=(?P<str>[^&]*)(&.*$|$)', jockeycode).groupdict()['str']
            else:
                jockeycode = None
            if _trainercode:
                trainercode = _trainercode[0]
                trainercode = re.match(r'^http://www.hkjc.com/english/racing/trainerprofile.asp?.*trainercode=(?P<str>[^&]*)(&.*$|$)', trainercode).groupdict()['str']
            else:
                trainercode = None

            #horse report
            racingincidentreport_ = response.xpath('//tr[td[contains(text(), "Racing Incident Report")]]/following-sibling::tr/td/text()').extract()
            racingincidentreport = racingincidentreport_ and racingincidentreport_[0]
            horsereport = getHorseReport(racingincidentreport, horsename)

            #agg functions
            winodds_d = OrderedDict(sorted(agg_winodds.items(), key=lambda t: t[0]))
            winoddsranks = OrderedDict(sorted(winodds_d.items(), key=lambda t: t[1]))
            winoddsrank = list(winoddsranks.keys()).index(horsecode)+1 #index at 0
            todaysrunners = list(winoddsranks.keys())
            #Unique Race Identity
            horseloader.add_value('racedate', todaysracedate_str)
            horseloader.add_value('racecoursecode', todaysracecoursecode)
            horseloader.add_value('racenumber', todaysracenumber)
            ###horse specific
            horseloader.add_value('horseno', horseno)
            horseloader.add_value('horsecode', horsecode)
            horseloader.add_value('jockeycode', jockeycode)
            horseloader.add_value('trainercode', trainercode)
            horseloader.add_value('place', place)
            horseloader.add_value('finishtime', str(finishtime))
            horseloader.add_value('actualwt', actualwt)
            horseloader.add_value('runningpositions', runningpositions)
            horseloader.add_value('lbw', str(lbw))
            horseloader.add_value('draw', draw)
            horseloader.add_value('winodds', str(winodds))
            horseloader.add_value('winoddsrank', winoddsrank)
            horseloader.add_value('todaysrunners', todaysrunners)
            horseloader.add_value('horsewt', horsewt)
            horseloader.add_value('timeperm', gettimeperlength(racedistance, finishtime))
            horseloader.add_value('horsereport', horsereport)


            logger.info("todaysracedate loop %s" % todaysracedate_str)
            logger.info("todaysracecoursecode loop %s" % todaysracecoursecode)
            logger.info("todaysracenumber loop %s" % todaysracenumber)
            logger.info("place loop %s" % place)
            logger.info("horseno loop %s" % horseno)
            logger.info("horsecode loop %s" % horsecode)
            logger.info("jockeycode loop %s" % jockeycode)
            logger.info("trainercode loop %s" % trainercode)
            logger.info("draw loop %s" % draw)
            logger.info("lbw loop %s" % lbw)
            logger.info("runningpositions loop %s" % runningpositions)
            logger.info("actualwt loop %s" % actualwt)
            logger.info("horse wt loop %s" % horsewt)
            logger.info("finishtimeloop %s" % finishtime)
            logger.info("winodds loop %s" % winodds)
            logger.info("winoddsrank %s-%s" % (horsecode, winoddsrank))
            logger.info("Time per m %s" % gettimeperlength(racedistance, finishtime))
            logger.info("horsereport %s -> %s: %s" % (horsecode, horsename, horsereport))

            horse_items += [horseloader.load_item()]

        yield scrapy.Request(
            hkjcres16_item['sectional_time_url'],
            self.parse_sectional_time,
            dont_filter=True, meta={
                # 'hkjcres16_item': hkjcres16_item,
                'horse_items': horse_items,
            })

    def parse_sectional_time(self, response):
        horse_lines_selector = response.xpath('//table[@class="bigborder"]//table//a/../../..')
        sectional_time_selector = response.xpath('//table[@class="bigborder"]//table//a/../../../following-sibling::tr[1]')

        horse_items = response.meta['horse_items']

        for line_selector, time_selector in zip(horse_lines_selector, sectional_time_selector):
            horse_name_cell = line_selector.xpath('td[3]/div/a/text()').extract()[0]
            horse_name_regexp = '^(?P<name>[^\(]+)\((?P<code>[^\)]+)\)$'
            horse_name_dict = re.match(horse_name_regexp, horse_name_cell).groupdict()
            horsename = horse_name_dict['name']
            horsecode = horse_name_dict['code']

            sec_timelist = [time.strip() for time in time_selector.xpath('td/text()').extract()]
            sec_timelist_len = len(sec_timelist)
            sec_timelist.extend([None for i in xrange(6-sec_timelist_len)])
            sec_timelist = map(get_sec_in_secs, sec_timelist)

            marginsbehindleader = [s.strip('\t\n\r ') for s in line_selector.xpath('td//table//td/text()').extract()]
            marginsbehindleader.extend([None]*(6 - len(marginsbehindleader)))
            marginsbehindleader = map(horselengthprocessor, marginsbehindleader)

            for horse in horse_items:
                if horse['horsecode'][0] == horsecode:
                    logger.info(horsecode)
                    horse['sec_timelist'] = sec_timelist
                    horse['marginsbehindleader'] = marginsbehindleader
                    break
            else:
                logger.info('Horse with code %s not found', horsecode)
                logger.info('%s', horse_items)

        for horse in horse_items:
            yield horse
