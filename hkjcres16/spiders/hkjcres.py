import scrapy
from scrapy.loader import ItemLoader
from hkjcres16.items import RaceItem, RunnerItem, HorseItem, VenueItem, JockeyItem, TrainerItem, OwnerItem
from scrapy.loader.processors import TakeFirst,Compose, MapCompose, Identity, Join
from urlparse import urlparse
from collections import defaultdict,OrderedDict, Counter
#from selenium import webdriver
#from time import sleep
import urllib
import pandas as pd
import re
import logging
import csv
from datetime import datetime
import itertools
from hkjcres16.utilities import *
import pprint
import numpy as np

from kitchen.text.converters import getwriter, to_bytes, to_unicode
from kitchen.i18n import get_translation_object


RE_VAL  = re.compile(r"^:*\s*")
T_PAT = re.compile(r'.*trainercode=([A-Z]{2,3})&.*')
J_PAT = re.compile(r'.*JockeyCode=([A-Z]{2,3})&.*')
RACENO_PAT = re.compile(r'.*raceno=([0-9]{1,2})&.*')
RACECOURSE_PAT = re.compile(r'.*venue=([A-Z]{2})$')

#600,000 1,500,000
raceprize_pat = re.compile("\D*HK$(\d{0,1}\,\d{3}\,\d{3}).*")
horsecode_pat = re.compile(r"horseno=(?P<str>.+)")

class DefaultListOrderedDict(OrderedDict):
    def __missing__(self,k):
        self[k] = []
        return self[k]

def divprocessor(divlist):
    return divprocessor

def timetofloat(t):
    return float("{0:.2f}".format(float(t)))

def dorunningpositions(l):
    return " ".join(l)


class JockeyItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class TrainerItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class OwnerItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class HorseItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

class VenueItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class RunnerItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    #default_output_processor = TakeFirst()
    # Race_item_in = Identity()
    # Race_item_out = Identity()
    # place_out = Join()
    # actualwt_out = Join()
    
    #runningpositions_out = Compose(dorunningpositions)

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
    # venue_in = Identity()
    # venue_out = Identity()

logger = logging.getLogger('hkjcres_application')

class HkjcresSpider(scrapy.Spider):
    name = "hkjcres"
    allowed_domains = ["racing.hkjc.com"]


    #input.csv
    def __init__(self, input_filename='input2.csv', *args, **kwargs):
        super(HkjcresSpider, self).__init__(*args, **kwargs)
        self.reference_date = datetime.today()
        with open(input_filename, 'rU') as f:
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

    '''
    Results Page

    '''
    def parse(self, response):
        logger.info('Results Page: A response from %s just arrived!', response.url)
        

        raceloader = RaceItemLoader(RaceItem(), response=response)
        item = RaceItem()

        if int(response.url.split('/')[-1]) > 9:
            todaysracenumber = '{}'.format(response.url.split('/')[-1])
        else:
            todaysracenumber = '{}'.format(response.url.split('/')[-1])
        #basic race information

        # item['url'] = response.url
        raceloader.add_value('url', response.url)

        raceindex_path = re.compile(r'\((\d+)\)')
        item['raceindex'] = response.selector.xpath('//div[@class="boldFont14 color_white trBgBlue"]//text()').re(r'\((\d+)\)')
        raceloader.add_value('raceindex', response.selector.xpath('//div[@class="boldFont14 color_white trBgBlue"]//text()').re(r'\((\d+)\)'))

        #race details table
        newraceinfo = response.xpath('//table[@class ="tableBorder0 font13"]//*[self::td or self::td/span]//text()').extract()

        try:
            raceclass_ = newraceinfo[0].replace('-', '').strip()
            print("raceclass", raceclass_)
        except IndexError:
            try_num = response.meta['try_num']
            if try_num >= self.settings.get('MAX_TRYS', 5):
                logger.info('Failed! Has reached the maximum number of attempts. %s', response.url)
                raise StopIteration

            logger.info('Add again to query %s', response.url)
            yield scrapy.Request(response.url, self.parse, dont_filter=True, meta={'try_num': try_num + 1})
            raise StopIteration

        going_ = response.xpath('//table[@class ="tableBorder0 font13"]//td[contains(text(),"Going")]/following-sibling::*/text()').extract()[0]
        
        # raceclass_ = newraceinfo[0].replace('-', '').strip()


        #### TRACK VENUE INFO
        venueloader = VenueItemLoader(VenueItem(), response=response)
        racesurface = response.xpath('//table[@class ="tableBorder0 font13"]//td[contains(text(),"Course")]/following-sibling::*/text()').extract()[0]
        is_awt = False
        if racesurface == "ALL WEATHER TRACK":
            is_awt = True
        going = get_goingabb(going_, racesurface)
        venueloader.add_value('isAWT', is_awt)
        venueloader.add_value('surface', racesurface)
        todaysracecoursecode = response.url.split('/')[-2]
        venueloader.add_value('racecoursecode', todaysracecoursecode)
        raceloader.add_value('venue', venueloader.load_item())


        racedistance = newraceinfo[1].split(u'-')[0].replace(u'm', u'').replace(u'M', u'').strip()
        newsectionaltimes = response.xpath('//table[@class ="tableBorder0 font13"]//td[text()="Sectional Time :"]/following-sibling::td/text()').extract()
        winningsecs = map(float, newsectionaltimes)
        finishtime = sum(winningsecs)

        raceprize__= " ".join(response.xpath("//table[@class ='tableBorder0 font13']//td[contains(text(),'HK$')]/text()").extract())
        raceprize_ = raceprize__.replace(",", "").replace("HK$", "")
        raceprize = pd.np.float( (raceprize_))
        raceloader.add_value('raceprize', raceprize)

        raceclass = get_raceclassabb(raceclass_)
        raceloader.add_value('raceclass', raceclass)
        
        raceloader.add_value('racedistance', racedistance)
        raceloader.add_value('finishtime', finishtime)
        raceloader.add_value('going', going)

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
        raceloader.add_value('racedate', datetime.strptime(data['racedate'], '%Y%M%d'))
        raceloader.add_value('racenumber', todaysracenumber)
        if todaysracedate >= compwinstartdate:
            div_info['A1'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A1']/following-sibling::td/text()").extract()
            div_info['A2'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A2']/following-sibling::td/text()").extract()
            div_info['A3'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A3']/following-sibling::td/text()").extract()
        #parse our TT DIV INFO and other PRIZES
        # 'tripletrio_combo_div': u'1,2>5,10/2,6,10/1,4,8 3,826,375.00'
        ttdiv = None
        ttconsdiv = None
        pat = re.compile(r".+\s([0-9]+,[0-9]+,[0-9]+.00)")
        if div_info['TRIPLE TRIO']:
            ## cannot always split like this
            
            try:
                ttdiv= re.match(pat,div_info['TRIPLE TRIO'][0] ).group(0)
            except (AttributeError, ValueError, TypeError):
                ttdiv = div_info['TRIPLE TRIO']
                #ttdiv_ = div_info['TRIPLE TRIO'][0].split(" ")[-1]
            # valueerrir ttdiv= float(ttdiv_.replace(',','')) e.g. 
            ## ttdiv= float(ttdiv_.replace(',',''))
            ## ValueError: invalid literal for float(): 31114/4714/129
            ## 3,11,14/4,7,14/1,2,9 17,438,530.00

        if div_info['TRIPLE TRIO(Consolation)']:
            try:
                ttconsdiv= re.match(pat,div_info['TRIPLE TRIO(Consolation)'][0] ).group(0)
            except (AttributeError, ValueError, TypeError):
                ttconsdiv = div_info['TRIPLE TRIO(Consolation)']
        #sectional urls
        # what happens if cant get sectional URL? Item raceloader will return null
        raceloader.add_value('sectional_time_url', response.xpath('//div[@class="rowDiv15"]/div[@class="rowDivRight"]/a/@href').extract())
        # raceloader.add_value('runnercodes', response.xpath('//table[@class="tableBorder trBgBlue tdAlignC number12 draggable"]//td[@class="tdAlignL font13 fontStyle"][1]/text()').extract())


        horsecode_pat = re.compile(r".*horseno=(?P<str>.+)")

        # logger.info(div_info)

        if div_info['TRIPLE TRIO']:
            todaysracenumber = int(todaysracenumber)
            ttraces = [todaysracenumber-2,todaysracenumber-1, todaysracenumber]
            ttprize = float(div_info['TRIPLE TRIO'][1].replace(",", ""))
            raceloader.add_value('ttraces', ttraces)
            raceloader.add_value('ttprize', ttprize) 


        raceloader.add_value('win_combo_div', div_info['WIN'])
        raceloader.add_value('place_combo_div', div_info['PLACE'])
        raceloader.add_value('qn_combo_div' , div_info['QUINELLA'])
        raceloader.add_value('qnp_combo_div' , div_info['QUINELLA PLACE'])
        raceloader.add_value('tce_combo_div' , div_info['TIERCE'])
        raceloader.add_value('trio_combo_div' , div_info['TRIO'])
        raceloader.add_value('f4_combo_div' , div_info['FIRST 4'])
        raceloader.add_value('qtt_combo_div' , div_info['QUARTET'])
        raceloader.add_value('dbl9_combo_div' , div_info['9TH DOUBLE'])
        raceloader.add_value('dbl8_combo_div' , div_info['8TH DOUBLE'])
        raceloader.add_value('dbl7_combo_div' , div_info['7TH DOUBLE'])
        raceloader.add_value('dbl6_combo_div' , div_info['6TH DOUBLE'])
        raceloader.add_value('dbl5_combo_div' , div_info['5TH DOUBLE'])
        raceloader.add_value('dbl4_combo_div' , div_info['4TH DOUBLE'])
        raceloader.add_value('dbl3_combo_div' , div_info['3RD DOUBLE'])
        raceloader.add_value('dbl2_combo_div' , div_info['2ND DOUBLE'])
        raceloader.add_value('dbl1_combo_div' , div_info['1ST DOUBLE'])
        raceloader.add_value('dbl10_combo_div' , div_info['10TH DOUBLE'])
        raceloader.add_value('dbltrio1_combo_div' , div_info['1ST DOUBLE TRIO'])
        raceloader.add_value('dbltrio2_combo_div' , div_info['2ND DOUBLE TRIO'])
        raceloader.add_value('dbltrio3_combo_div' , div_info['3RD DOUBLE TRIO'])
        raceloader.add_value('tripletriocons_combo_div' , div_info['TRIPLE TRIO(Consolation)'])
        raceloader.add_value('tripletrio_combo_div', div_info['TRIPLE TRIO'])
        raceloader.add_value('a1_div', div_info['A1'])
        raceloader.add_value('a2_div', div_info['A2'])
        raceloader.add_value('a3_div', div_info['A3'])
        raceloader.add_value('sixup_combo_div', div_info['SIX UP'])
        raceloader.add_value('jockeychallenge_combo_div', div_info['JOCKEY CHALLENGE'])
        

        # sectional_time_url_ = response.xpath('//div[@class="rowDiv15"]/div[@class="rowDivRight"]/a[@href]').extract()
        # for sel in response.xpath('//ul/li'):
        #
        #     raceloader.add_xpath('title', 'a/text()')
        #     raceloader.add_xpath('link', 'a/@href')
        #     raceloader.add_xpath('desc', 'text()')
        # return item


        

        horse_items = []

        ## winodds, lbw, finishtime
        trainerprizes = defaultdict(int)
        agg_winodds = defaultdict(float)


        # pos1 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgGrey']//td[1]/text()").extract()
        # pos2 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgWhite']//td[1]/text()").extract()
        horsecodes1 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgGrey']//td[3]/a/@href").extract()
        horsecodes2 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgWhite']//td[3]/a/@href").extract()
        horsecodes_ = horsecodes1 + horsecodes2
        horsecodes = [ re.match(horsecode_pat, x).groupdict()['str'] for x in horsecodes_]
        
        print("horsecodes", horsecodes)
        # poss_ = pos1 + pos2
        # pprint.pprint(poss_)
        #find indexes of all pos with 
        allplaces1 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgGrey']/td[1]/text()").extract()
        allplaces2 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgWhite']/td[1]/text()").extract()
        allplaces_ = allplaces1 + allplaces2
        allplaces = [ processplace(x) for x in allplaces_]
        started_idxs = [i for i,x in enumerate(allplaces) if not isscratched(x)]
        print("started_idxs", started_idxs)
        horsecodes_started = [ h for i,h in enumerate(horsecodes) if i in started_idxs ]
        scratchedlist = [ h for i,h in enumerate(horsecodes) if i not in started_idxs ]


        allsps1 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgGrey']//td[12]/text()").extract()
        allsps2 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgWhite']//td[12]/text()").extract()
        allsps_ = allsps1 + allsps2
        allsps_started = [ float(x) for x in allsps_ if x != '---' ]
        
        for hc, sp in zip(horsecodes_started, allsps_started):
            agg_winodds[hc]= sp

        spsinorder = sorted(agg_winodds.iteritems(),key=lambda (k,v): v)
        # spsinorder = OrderedDict(sorted(agg_winodds.items(), key=lambda t: t[1]))
        # print("spsinorder", spsinorder)




        trainer_pat = re.compile(r'^http://www.hkjc.com/english/racing/trainerprofile.asp?.*trainercode=(?P<str>[^&]*)(&.*$|$)')


        allts_1 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgGrey']//td[5]//a/@href").extract()
        allts_2 = response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgWhite']//td[5]//a/@href").extract()
       
        allts_ = allts_1 + allts_2
        allts = [ re.match(trainer_pat, t).groupdict()['str'] for t in allts_ if t is not None] 
        # print(allts)

        #agg functions
        # print(agg_winodds.items())
        # winodds_d = OrderedDict(sorted(agg_winodds.items(), key=lambda t: t[0]))
        # winoddsranks = OrderedDict(sorted(winodds_d.items(), key=lambda t: t[1]))
        # todaysrunners = list(winoddsranks.keys()) #how to get each horse having all 
        

        for t,p in zip(allts, allplaces):
            prize = getnethorseprize(p, raceprize)
            # print("tcode, prize %s %s" % (t, prize))
            trainerprizes[t] += getnethorseprize(p, raceprize)
        
        #RACE SPECIFIC AGGR trainerprizes, winoddsranks, runnerslist
        raceloader.add_value("trainersprizes", trainerprizes)
        raceloader.add_value("starterslist", horsecodes_started)
        raceloader.add_value("scratchedlist", scratchedlist)
        Race_item = raceloader.load_item()


        racedayurl = 'http://racing.hkjc.com/racing/Info/Meeting/RaceCard'\
            '/English/Local/{racedate}/{coursecode}/1'.format(
                racedate=todaysracedate_str,
                coursecode=todaysracecoursecode,
        )

        # print(racedayurl)
        # print("ALL TRAINERS PRIZES")
        # pprint.pprint(trainerprizes)

        ##RUNNERS TABLE
        allplaces_ = list()
        for i,row in enumerate(response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgGrey']")):
            
            jockeyloader = JockeyItemLoader(JockeyItem(), response=response)
            trainerloader = TrainerItemLoader(TrainerItem(), response=response)
            ownerloader = OwnerItemLoader(OwnerItem(), response=response)
            
            runnerloader = RunnerItemLoader(RunnerItem())

            runnerloader.add_value('Race_item', Race_item)
            # horsecode = horsecode_pat.findall(row.xpath('./td[3]/a/@href').extract()[0]) or None

            horseurl = row.xpath('./td[3]/a/@href').extract()[0]
            # <a href="http://www.hkjc.com/english/racing/horse.asp?horseno=S436">SMART DECLARATION</a>
            horsecode = re.match(horsecode_pat, horseurl).groupdict()['str']


            horsename = row.xpath('./td[3]/a/text()').extract()[0]
            if row.xpath('./td[1]/text()').extract():
                place = row.xpath('./td[1]/text()').extract()[0]
            else:
                place = 99

            _horseno= row.xpath("./td[2]/text()").extract()
            horseno = _horseno[0] if _horseno else 99
            actualwt = row.xpath('./td[6]//text()').extract()[0]
            horsewt = row.xpath('./td[7]//text()').extract()[0]
            draw_ = row.xpath('./td[8]//text()').extract()[0]
            if draw_ == '---' or draw_ == '--':
                draw = 99
            else:
                draw = int(draw_)
            lbw = horselengthprocessor(row.xpath('./td[9]//text()').extract()[0])
            winodds = getodds(row.xpath('./td[12]/text()').extract()[0])

            if type(horsecode)== type([]):
                horsecode = horsecode[0]
            if winodds == '---' or not winodds:
                winodds = 99
                winoddsrank = None
            else:
                #tuples
                # winoddsrank = (spsinorder[0].index(horsecode))+1
                winoddsrank = [i for i,x in enumerate(spsinorder) if x[0] == horsecode]
                winoddsrank[0] += 1

            
            SeasonalBrandNo = horsecode[0]
            finishtime = get_sec(row.xpath('./td[11]/text()').extract()[0])
            runningpositions = " ".join(row.xpath('./td[10]/table//td//text()').extract())

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
            if trainercode:
                trainerprize = trainerprizes[trainercode] 
            horseprize = getnethorseprize(place, raceprize)
            
            runnerloader.add_value('horseprize', horseprize)
            runnerloader.add_value('trainerprize', trainerprize)
            #horse report
            racingincidentreport_ = response.xpath('//tr[td[contains(text(), "Racing Incident Report")]]/following-sibling::tr/td/text()').extract()
            racingincidentreport = racingincidentreport_ and racingincidentreport_[0]
            horsereport = getHorseReport(racingincidentreport, horsename)


            
            #Identity
            runnerloader.add_value('racedate', todaysracedate_str)
            runnerloader.add_value('racenumber', todaysracenumber)
            
            ###horse specific
            runnerloader.add_value('horseno', horseno)
            runnerloader.add_value('horsecode', horsecode)
            runnerloader.add_value('horseurl', horseurl)
            runnerloader.add_value('jockeycode', jockeycode)
            
            runnerloader.add_value('trainercode', trainercode)

            runnerloader.add_value('place', place)
            runnerloader.add_value('finishtime', finishtime)
            runnerloader.add_value('actualwt', actualwt)
            runnerloader.add_value('runningpositions', runningpositions)
            runnerloader.add_value('lbw', str(lbw))
            runnerloader.add_value('draw', draw)
            runnerloader.add_value('winodds', float(winodds))
            runnerloader.add_value('seasonalbrandno', SeasonalBrandNo)
            runnerloader.add_value('horsewt', horsewt)
            runnerloader.add_value('winoddsrank', winoddsrank)

            runnerloader.add_value('timeperm', str(gettimeperlength(racedistance, finishtime)))
            runnerloader.add_value('horsereport', horsereport)
            runnerloader.add_value('seasonalbrandno', SeasonalBrandNo)

            jockeyloader.add_value('jockeycode', jockeycode)
            trainerloader.add_value('trainercode', trainercode)

            runnerloader.add_value('trainer', trainerloader.load_item())
            runnerloader.add_value('jockey', jockeyloader.load_item())
            # logger.info("todaysracedate loop %s" % todaysracedate_str)
            # logger.info("todaysracecoursecode loop %s" % todaysracecoursecode)
            # logger.info("todaysracenumber loop %s" % todaysracenumber)
            # logger.info("place loop %s" % place)
            # logger.info("horseno loop %s" % horseno)
            # logger.info("horsecode loop %s" % horsecode)
            # logger.info("jockeycode loop %s" % jockeycode)
            # logger.info("trainercode loop %s" % trainercode)
            # logger.info("draw loop %s" % draw)
            # logger.info("lbw loop %s" % lbw)
            # logger.info("runningpositions loop %s" % runningpositions)
            # logger.info("actualwt loop %s" % actualwt)
            # logger.info("horse wt loop %s" % horsewt)
            # logger.info("jtohweight loop %s" % getjtohweight(actualwt, horsewt))
            # logger.info("finishtimeloop %s" % finishtime)
            # logger.info("winodds loop %s" % winodds)
            # logger.info("ttdiv consdiv loop %s- %s" % (ttdiv, ttconsdiv))

            horse_items += [runnerloader.load_item()]


        for row in response.xpath("//table[@class='tableBorder trBgBlue tdAlignC number12 draggable']//tr[@class='trBgWhite']"):

            jockeyloader = JockeyItemLoader(JockeyItem(), response=response)
            trainerloader = TrainerItemLoader(TrainerItem(), response=response)
            ownerloader = OwnerItemLoader(OwnerItem(), response=response)

            runnerloader = RunnerItemLoader(RunnerItem())
            runnerloader.add_value('Race_item', Race_item)

            horseurl = row.xpath('./td[3]/a/@href').extract()[0]
            horsecode = re.match(horsecode_pat, horseurl).groupdict()['str']


            # winoddsrank = list(winoddsranks.keys()).index(horsecode) #index at 0
            # winoddsrank +=1
            horsename = row.xpath('./td[3]/a/text()').extract()[0]
            horseurl =  row.xpath('./td[3]/a/@href').extract()[0]

            if row.xpath('./td[1]/text()').extract():
                place = row.xpath('./td[1]/text()').extract()[0]
            else:
                place = 99

            horseno= row.xpath("./td[2]/text()").extract()
            _horseno= row.xpath("./td[2]/text()").extract()
            horseno = _horseno[0] if _horseno else 99
            actualwt = float(row.xpath('./td[6]//text()').extract()[0])
            horsewt = row.xpath('./td[7]//text()').extract()[0]
            draw_ = row.xpath('./td[8]//text()').extract()[0]
            if draw_ == '---' or draw_ == '--':
                draw = 99
            else:
                draw = int(draw_)
            lbw = horselengthprocessor(row.xpath('./td[9]//text()').extract()[0])
            winodds = getodds(row.xpath('./td[12]/text()').extract()[0])
            
            if type(horsecode)== type([]):
                horsecode = horsecode[0]
            if winodds == '---' or not winodds:
                winodds = 99
                winoddsrank = None
            else:
                winoddsrank = [i+1 for i,x in enumerate(spsinorder) if x[0] == horsecode]
                # winoddsrank[0] += 1
                # winoddsrank = (spsinorder[0].index(horsecode))+1




            SeasonalBrandNo = horsecode[0]
            finishtime = get_sec(row.xpath('./td[11]/text()').extract()[0])
            horsetimepermeter = None
            if finishtime:
                horsetimepermeter = round( float(racedistance)/float(finishtime), 3)
            # print("horsetimepermeter -->", horsetimepermeter )
            runningpositions = " ".join(row.xpath('./td[10]/table//td//text()').extract())

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
            if trainercode:
                trainerprize = trainerprizes[trainercode]
            horseprize = getnethorseprize(place, raceprize)
            runnerloader.add_value('horseprize', horseprize)
            runnerloader.add_value('trainerprize', trainerprize)
            #horse report
            racingincidentreport_ = response.xpath('//tr[td[contains(text(), "Racing Incident Report")]]/following-sibling::tr/td/text()').extract()
            racingincidentreport = racingincidentreport_ and racingincidentreport_[0]
            horsereport = getHorseReport(racingincidentreport, horsename)
            horseurl = "http://www.hkjc.com/english/racing/horse.asp?HorseNo={}&Option=1#htop".format(horsecode)

            #Unique Race Identity
            runnerloader.add_value('racedate', todaysracedate_str)
            # runnerloader.add_value('racecoursecode', todaysracecoursecode)
            runnerloader.add_value('racenumber', todaysracenumber)
            ###horse specific
            runnerloader.add_value('horseno', horseno)
            runnerloader.add_value('horsecode', horsecode)
            runnerloader.add_value('horseurl', horseurl)
            runnerloader.add_value('jockeycode', jockeycode)
            runnerloader.add_value('trainercode', trainercode)
            runnerloader.add_value('place', place)
            runnerloader.add_value('finishtime', str(finishtime))
            runnerloader.add_value('horsetimepermeter', horsetimepermeter)
            runnerloader.add_value('actualwt', actualwt)
            runnerloader.add_value('runningpositions', runningpositions)
            runnerloader.add_value('lbw', str(lbw))
            runnerloader.add_value('draw', draw)
            runnerloader.add_value('winodds', float(winodds))
            runnerloader.add_value('seasonalbrandno', SeasonalBrandNo)

            if winodds:
                runnerloader.add_value('oddschance', round(1/winodds,3))
            runnerloader.add_value('winoddsrank', winoddsrank)

            if horsewt == '-':
                horsewt = None 
            runnerloader.add_value('horsewt', horsewt)

            # runnerloader.add_value('timeperm', str(gettimeperlength(racedistance, finishtime)))
            runnerloader.add_value('horsereport', horsereport)
            jockeyloader.add_value('jockeycode', jockeycode)
            trainerloader.add_value('trainercode', trainercode)
            runnerloader.add_value('trainer', trainerloader.load_item())
            runnerloader.add_value('jockey', jockeyloader.load_item())
            # logger.info("todaysracedate loop %s" % todaysracedate_str)
            # logger.info("todaysracecoursecode loop %s" % todaysracecoursecode)
            # logger.info("todaysracenumber loop %s" % todaysracenumber)
            # logger.info("place loop %s" % place)
            # logger.info("horseno loop %s" % horseno)
            # logger.info("horsecode loop %s" % horsecode)
            # logger.info("jockeycode loop %s" % jockeycode)
            # logger.info("trainercode loop %s" % trainercode)
            # logger.info("draw loop %s" % draw)
            # logger.info("lbw loop %s" % lbw)
            # logger.info("runningpositions loop %s" % runningpositions)
            # logger.info("actualwt loop %s" % actualwt)
            # logger.info("horse wt loop %s" % horsewt)
            # logger.info("jtohweight loop %s" % getjtohweight(actualwt, horsewt))
            # logger.info("finishtimeloop %s" % finishtime)
            # logger.info("winodds loop %s" % winodds)
            # logger.info("winoddsrank %s-%s" % (horsecode, winoddsrank))
            # logger.info("Time per m %s" % gettimeperlength(racedistance, finishtime))
            # logger.info("horsereport %s -> %s: %s" % (horsecode, horsename, horsereport))
            
            horse_items += [runnerloader.load_item()]

        #LIST OF HORSES FROM RESULTS INCL RACE DATA
        #F TO 1 SECTIONALS PAGE
        # yield scrapy.Request(
        #     Race_item['sectional_time_url'],
        #     self.parse_sectional_time,
        #     dont_filter=True, 
        #     meta={
        #         'horse_items': horse_items,
         
        #     })

        yield scrapy.Request(
            racedayurl,
            self.parse_raceday,
            dont_filter=True, 
            meta={
                'horse_items': horse_items,
                'sectional_time_url': Race_item['sectional_time_url'],
            })

    #gear priority seasonstakes
    def parse_raceday(self, response):
        print "in raceday"
        horse_items = response.meta['horse_items']
        racedayinfo = defaultdict(dict)
        for tr in response.xpath('//table[@class="draggable hiddenable"]//tr[position() > 1]'):
            horsecode_ = tr.xpath('td[4]/a/@href').extract()[0]
            horsecode = re.match(r"^[^\?]+\?horseno=(?P<code>\w+)'.*$",
                    horsecode_).groupdict()['code']

            todaysratingchange_ = tr.xpath('td[12]/text()').extract()[0]
            gear_ = tr.xpath('td[21]/text()').extract()[0]
            seasonstakes_ = tr.xpath('td[19]/text()').extract()[0]
            priority_ = get_prio_val(tr.xpath('td[20]/text()').extract()[0].strip())
            racedayinfo[horsecode] = {'todaysratingchange': todaysratingchange_, 'gear': gear_, 'seasonstakes': seasonstakes_, 'priority': priority_}
        yield scrapy.Request(
            response.meta['sectional_time_url'],
            self.parse_sectional_time,
            dont_filter=True, 
            meta={
                'horse_items': horse_items,
                'racedayinfo': racedayinfo,
        
            })

    # sort out trainerprizes and do parse_horse

    def parse_sectional_time(self, response):
       
        horse_lines_selector = response.xpath('//table[@class="bigborder"]//table//a/../../..')
        sectional_time_selector = response.xpath('//table[@class="bigborder"]//table//a/../../../following-sibling::tr[1]')

        horse_items = response.meta['horse_items']
        racedayinfo = response.meta['racedayinfo']
 
        sectionalsinfo = defaultdict(dict)

        for line_selector, time_selector in zip(horse_lines_selector, sectional_time_selector):
            horse_name_cell = line_selector.xpath('td[3]/div/a/text()').extract()[0]
            horse_name_regexp = '^(?P<name>[^\(]+)\((?P<code>[^\)]+)\)$'
            horse_name_dict = re.match(horse_name_regexp, horse_name_cell).groupdict()
            horsename = horse_name_dict['name']
            horsecode = horse_name_dict['code']

            horseurl = "http://www.hkjc.com/english/racing/horse.asp?HorseNo={}&Option=1#htop".format(horsecode)
            cn_horseurl = "http://www.hkjc.com/chinese/racing/horse.asp?HorseNo={}&Option=1#htop".format(horsecode)
            secfinishtime = line_selector.xpath('td[10]/div/text()').extract()[0]

            sec_timelist = [time.strip() for time in time_selector.xpath('td/text()').extract()]
            sec_timelist_len = len(sec_timelist)
            sec_timelist.extend([None for i in xrange(6-sec_timelist_len)])
            sec_timelist = map(get_sec_in_secs, sec_timelist)
            sec_vars = {}
            for i,s in enumerate(sec_timelist):
                sec_vars[str(i+1)] = s

            marginsbehindleader = [s.strip('\t\n\r ') for s in line_selector.xpath('td//table//td/text()').extract()]
            marginsbehindleader.extend([None]*(6 - len(marginsbehindleader)))
            marginsbehindleader = map(horselengthprocessor, marginsbehindleader)
            marg_vars = {}
            for i,s in enumerate(sec_timelist):
                marg_vars[str(i+1)] = s

            sectionalsinfo[horsecode] = {
            'horsename': horsename, 
            'sec_timelist': sec_timelist, 
            'marginsbehindleader': marginsbehindleader,
            'sec1': sec_vars['1'],
            'sec2': sec_vars['2'],
            'sec3': sec_vars['3'],
            'sec4': sec_vars['4'],
            'sec5': sec_vars['5'],
            'sec6': sec_vars['6'],
            'margin1': marg_vars['1'],
            'margin2': marg_vars['2'],
            'margin3': marg_vars['3'],
            'margin4': marg_vars['4'],
            'margin5': marg_vars['5'],
            'margin6': marg_vars['6'],
            'horseurl': horseurl}

        # this horsecode
            request = scrapy.Request(cn_horseurl, callback=self.parsecnhorse, dont_filter=True, 
                meta={
                'horse_items': horse_items ,
                'sectionalsinfo': sectionalsinfo,
                'racedayinfo': racedayinfo,
                })
            # meta_dict = response.meta
            # meta_dict.update(sectionalsinfo)
            # request.meta.update(meta_dict)

            yield request


        # logger.info(sectionalsinfo)

            # logger.info("in sectionals zip loop")
            # pprint.pprint(horsecode) 
            # pprint.pprint(sec_timelist)
            # pprint.pprint(marginsbehindleader)

            # for horse in horse_items:
            #     if horse['horsecode'] == horsecode:
            #         # logger.info(horsecode)
            #         horse['sec_timelist'] = sec_timelist
            #         # logger.info(sec_timelist)
            #         horse['marginsbehindleader'] = marginsbehindleader
            #         horse['secfinishtime'] = secfinishtime
            #         break
            #     else:
            #         logger.info('Horse not found in Sectionals with code %s', horsecode)
            #         logger.info('%s', horse_items)
            # for horse in horse_items:
            #     thishorsecode = horse['horsecode']
            #     horse['sec_timelist'] = sectionalsinfo[thishorsecode]['sec_timelist']
            #     yield horse

            # for horse in horse_items:

            #     yield scrapy.Request(
            #         horseurl,
            #         self.parse_horse,
            #         dont_filter=True,
                    
            #         meta = {
            #                 'horse': horse,
            #                 'trainerprizes': trainerprizes
            #                 }
            #         )

            # for horse in horse_items:

            #     yield scrapy.Request(
            #     horseurl,
            #     self.parse_horse,
            #     dont_filter=True,
            #     meta = {
            #         'horse': horse,
            #         'trainerprizes': trainerprizes
            #     }
            #     )
            # yield horse

    def parsecnhorse(self, response):
        
        cn_horse_name = tf(response.css(".subsubheader .title_text").xpath("text()").extract()).split("\xc2\xa0")[0].strip()
        print(u'cn_horse_name: %s') % to_unicode(cn_horse_name)
        # print(cn_horse_name, cn_horsename2)
        horse_items = response.meta['horse_items']
        sectionalsinfo = response.meta['sectionalsinfo']
        racedayinfo = response.meta['racedayinfo']
        for horse in horse_items:
            thishorsecode = horse['horsecode']
            print thishorsecode
            print sectionalsinfo[thishorsecode]
            horse['chinesename'] = to_unicode(cn_horse_name)
            horsecode = horse['horsecode']
            horseurl = "http://www.hkjc.com/english/racing/horse.asp?HorseNo={}&Option=1#htop".format(horsecode)
            if sectionalsinfo[thishorsecode]:
                horse['sec_timelist'] = sectionalsinfo[thishorsecode]['sec_timelist']
                horse['marginsbehindleader'] = sectionalsinfo[thishorsecode]['marginsbehindleader']
                horse['sec1'] = sectionalsinfo[thishorsecode]['sec1']
                horse['sec2'] = sectionalsinfo[thishorsecode]['sec2']
                horse['sec3'] = sectionalsinfo[thishorsecode]['sec3']
                horse['sec4'] = sectionalsinfo[thishorsecode]['sec4']
                horse['sec5'] = sectionalsinfo[thishorsecode]['sec5']
                horse['sec6'] = sectionalsinfo[thishorsecode]['sec6']
                horse['margin1'] = sectionalsinfo[thishorsecode]['margin1']
                horse['margin2'] = sectionalsinfo[thishorsecode]['margin2']
                horse['margin3'] = sectionalsinfo[thishorsecode]['margin3']
                horse['margin4'] = sectionalsinfo[thishorsecode]['margin4']
                horse['margin5'] = sectionalsinfo[thishorsecode]['margin5']
                horse['margin6'] = sectionalsinfo[thishorsecode]['margin6']
            horse['gear'] = horse['priority']=horse['seasonstakes']=horse['todaysratingchange']= None
            if racedayinfo[thishorsecode]:
                horse['priority'] = racedayinfo[thishorsecode]['priority']
                horse['gear'] = racedayinfo[thishorsecode]['gear']
                horse['seasonstakes'] = racedayinfo[thishorsecode]['seasonstakes']
                horse['todaysratingchange'] = racedayinfo[thishorsecode]['todaysratingchange']
            # yield horse
            yield scrapy.Request(
                horseurl,
                self.parse_horse,
                dont_filter=True,
                meta = {
                    'horse': horse,
                    }
            )


    def parse_horse(self, response):

        print "IN HORSE\n"
        pprint.pprint(response.meta['horse'])
        print(response.url)

        horsecode = response.meta['horse']['horsecode']
        todaysracedate = datetime.strptime(response.meta['horse']['Race_item']['racedate'], '%Y%m%d').date()
        todaysdistance = response.meta['horse']['Race_item']['racedistance']
        todaysclass = response.meta['horse']['Race_item']['raceclass']
        todaystrainercode = response.meta['horse']['trainercode']
        todaysgear = response.meta['horse']['gear']

        print("todaysdistance", todaysdistance)
        print(horsecode, todaysracedate)

        MAX_ROWS = 9999

        tw_url = "http://www.hkjc.com/english/racing/Track_Result.asp?txtHorse_BrandNo={}".format(horsecode)
        vet_url= "http://www.hkjc.com/english/racing/ove_horse.asp?HorseNo={}".format(horsecode)

        runhistory = defaultdict(list)

        samesirecodes = []
        # try:
        horse_name = tf(response.css(".subsubheader .title_eng_text").xpath("text()").extract()).split("\xc2\xa0")[0].strip()
        age = RE_VAL.sub("", tf(response.xpath("//font[contains(text(),'Country') and contains(text(),'Origin')]/../following-sibling::td[1]/font/text()").extract())).split("/")[1]
        country_of_origin = countryoforigin= RE_VAL.sub("", tf(response.xpath("//font[contains(text(),'Country') and contains(text(),'Origin')]/../following-sibling::td[1]/font/text()").extract())).split("/")[0].strip()
        year_of_birth = getdateofbirth(self.reference_date,int(age.strip()), country_of_origin)
        sirecodes = response.xpath("//select[@name='SIRE']/option/@value").extract()
        samesirecodes = [s.strip() for s in sirecodes]

        #URLS
        pedigree_url = None
        if response.xpath("//a[contains(text(), 'Pedigree')]/@href").extract():
            pedigree_url = response.xpath("//a[contains(text(), 'Pedigree')]/@href").extract()[0].strip()
            print pedigree_url
            pedigree_url = urljoin('http://www.hkjc.com/', pedigree_url.replace(u'..', u'english'))
        meta2 = dict(horsecode=horsecode,
                    horsename=horse_name,
                    yob= year_of_birth,
                    samesirecodes= samesirecodes,
                    countryoforigin= country_of_origin,
                    twurl = tw_url,
                    veturl = vet_url,
                    pedigreeurl= pedigree_url,
                    importtype=RE_VAL.sub("", tf(response.xpath("//font[contains(text(),'Import') and contains(text(),'Type')]/../following-sibling::td[1]/font/text()").extract())),
                    owner=tf(response.xpath("//font[text()='Owner']/../following-sibling::td[1]/font/a/text()").extract()),
                    sirename=tf(response.xpath("//font[text()='Sire']/../following-sibling::td[1]/font/a/text()").extract()),
                    damname=RE_VAL.sub("", tf(response.xpath("//font[text()='Dam']/../following-sibling::td[1]/font/text()").extract())),
                    damsirename=RE_VAL.sub("", tf(response.xpath("//font[text()=\"Dam's Sire\"]/../following-sibling::td[1]/font/text()").extract())))
        horse_item = HorseItem(**meta2)
        response.meta['horse']['horse'] = horse_item
        # pprint.pprint(meta2)
        # horseloader = HorseItemLoader(HorseItem(), response=response)

        #results table
        #per row
        pastraceindexes = list()
        pastracedates = list()
        pastplaces = list()
        pastdistances= list()
        pastgoings= list()
        pastraceclasses= list()
        pasttrainers= list()
        pastjockeys= list()
        pastrps= list()
        pastfinishtimes= list()
        pasthorseweights= list()
        pastgears= list()
        pastracecourses= list()
        pastsurfaceconfigs= list()
        pastraceconfigs = list()

        results_table = response.xpath("//table[@class='bigborder']//tr[ @bgcolor and not(@height) and not(@width) and position()>1]")
        maxi = 0
        l3racepoints = 0

        alltrainers = set()
        pastracedates_ = response.xpath("//table[@class='bigborder']//tr[ @bgcolor and not(@height) and not(@width) and position()>1]//td[position()=3 and normalize-space(text())]/text()").extract()
        pastracedates = [datetime.strptime(h_racedate, "%d/%m/%y").date() for h_racedate in pastracedates_]
        # pastracedates2 = [d for d in pastracedates if d < todaysracedate]
        firstraceindex = pastracedates.index(todaysracedate) + 1
            # print(pastracedates)
            # print(firstraceindex)

            #do until MAX_ROWS
        for i, row in enumerate(results_table):
            try: 
                row.xpath("td")[0].xpath("a/text()").extract()[0]
            except IndexError:
                continue
            if i < firstraceindex:
                continue
            if i < MAX_ROWS:
        #     #cutoff point
                maxi = i
        #         #collect
                # print(row)
                #issue need to exclude season rows
                h_raceindex = row.xpath("td")[0].xpath("a/text()").extract()
                #check for "Overseas" and ignore
                h_racenumberracecourse= row.xpath("td")[0].xpath("a/@href").extract()[0].strip()
                h_raceno = re.match(RACENO_PAT, h_racenumberracecourse).group(1)
                h_racecourse = re.match(RACECOURSE_PAT, h_racenumberracecourse).group(1)
                
                pastraceindexes.extend(h_raceindex)
                h_racedate = row.xpath("td")[2].xpath("text()").extract()[0]
                pastracedates.extend(h_racedate)
                h_racedateobj = datetime.strptime(h_racedate, "%d/%m/%y").date()
                urlracedate = datetime.strftime(h_racedateobj, "%Y%m%d") 
                
                # racevideofull_url = "http://racing.hkjc.com/racing/video/play.asp?type=replay-full&date={0}&no={1}&lang=eng".format(urlracedate,h_raceno)
                # racevideoaerial_url = "http://racing.hkjc.com/racing/video/aerial.aspx?date={0}&no={1}&lang=eng".format(urlracedate,h_raceno)
                # print(racevideofull_url,racevideoaerial_url)
                #place, #ractrackcourse, #dist, #going..#class, #draw, ....trainer

                h_place = processplace(row.xpath("td")[1].xpath("*//text()").extract()[0].strip())
                # pastplaces.append(h_place)

                ##AWT? isAWT
                h_rctrackcourse = row.xpath("td")[3].xpath("text()").extract()[0].strip()
                
                h_distance = int(row.xpath("td")[4].xpath("text()").extract()[0].strip())
                h_going = row.xpath("td")[5].xpath("text()").extract()[0].strip()
                h_raceclass = row.xpath("td")[6].xpath("text()").extract()[0].strip()
                h_draw = try_int(row.xpath("td")[7].xpath("font").xpath("text()").extract()[0].strip())
                h_rating = try_int(row.xpath("td")[8].xpath("text()").extract()[0].strip())

                ##JOCKEYS AND TRAINERS
                try:
                    h_trainer_ = " ".join(row.xpath("td")[9].xpath("a/@href").extract()).strip()
                    h_trainer = re.match(T_PAT, h_trainer_).group(1)
                except AttributeError:
                    h_trainer = " ".join(row.xpath("td")[9].xpath("text()").extract()).strip()
                alltrainers.add(h_trainer)
                #j may not be linked
                try:
                    h_jockey_ = " ".join(row.xpath("td")[10].xpath("a/@href").extract()).strip()
                    h_jockey = re.match(J_PAT, h_jockey_).group(1)
                except AttributeError:
                    h_jockey = " ".join(row.xpath("td")[10].xpath("text()").extract()).strip()
                    # h_jockey = " ".join(row.xpath("td")[10].xpath("text()").extract()).strip()
                # print(h_distance)
                # print(h_distance,h_going,h_raceclass,h_draw,h_rating, h_trainer,
                # h_jockey)
                runhistory[h_racedateobj].extend([h_place, h_distance,h_going,h_raceclass,h_draw,h_rating, h_trainer,h_jockey])

                h_lbw_ =  row.xpath("td")[11].xpath("*/text()| text()").extract()[0].strip()
                h_lbw = horselengthprocessor(h_lbw_)
                h_winodds_ =  row.xpath("td")[12].xpath("text()").extract()[0].strip()
                h_winodds = getodds(h_winodds_)
                h_actwt =  row.xpath("td")[13].xpath("text()").extract()[0].strip()
                h_rp = " ".join(row.xpath("td")[14].xpath("*//text()").extract()).strip().replace(unichr(160), "")
                h_finishtime_ = row.xpath("td")[15].xpath("text()").extract()[0].strip()
                h_finishtime = get_sec(h_finishtime_)
                h_horseweight = try_int(row.xpath("td")[16].xpath("text()").extract()[0].strip())
                h_gear = row.xpath("td")[17].xpath("text()").extract()[0].strip()


                # print(h_lbw, h_winodds, h_actwt, h_rp, h_finishtime, h_horseweight, h_gear)
                runhistory[h_racedateobj].extend([h_lbw, h_winodds, h_actwt, h_rp, h_finishtime, h_horseweight, h_gear])
                ##LTO CHanges
                if i in [firstraceindex, firstraceindex+1, firstraceindex+2]:
                    ##last 3 stats
                    l3racepoints+= getpoints(h_place)
                    response.meta['horse']['l3racepoints']=l3racepoints
                if i == firstraceindex:
                    # print (todaystrainercode, h_trainer, h_distance, todaysdistance, h_racedateobj)
                    print(h_trainer)
                    LTONewTrainer = h_trainer != todaystrainercode
                    LTODistanceChange = todaysdistance - h_distance
                    DaysSinceLastRun = (todaysracedate- h_racedateobj).days
                    response.meta['horse']['LTONewTrainer'] = LTONewTrainer
                    response.meta['horse']['LTODistanceChange'] = LTODistanceChange
                    response.meta['horse']['DaysSinceLastRun'] = DaysSinceLastRun
                    response.meta['horse']['GearLTOChange'] = comparegears(todaysgear, h_gear)

                        # gearChange = h_gear != response.meta['horse']['gear']
                        #classdropper
                        # LTOClassChange = getclasschange(todaysclass, h_raceclass)
                        # print(LTONewTrainer, LTODistanceChange, DaysSinceLastRun, DaysSinceLastRun<7)
            # runhistory_sorteddesc = sorted(runhistory.items(),lambda a, b: a[0] < b[0])

            #how to sort?
        response.meta['horse']['previousruns'] = runhistory
        response.meta['horse']['nooftrainers'] = len(alltrainers)
        runhistory_starts= {k:v for (k,v) in runhistory.iteritems() if v[0] != 99}
        # runhistory_starts = {k:v for k,v in runhistory if v[0] != 99}
        # runhistory_starts = {k:v for k,v in { k:list(filter(lambda i: i[0] != 99 ,v)) for k, v in runhistory.items()}.items() if len(v)}
        pprint.pprint(runhistory_starts)

        starts = len(runhistory_starts)
        allruns = len(runhistory)
        print("Starts", starts)
        

        
        #h_place, h_distance,h_going,h_raceclass,h_draw,h_rating, h_trainer,h_jockey,h_lbw, h_winodds, h_actwt, h_rp, h_finishtime, h_horseweight, h_gear
        nononevals = [x for x in runhistory.values() if x is not None]
        noWins = sum([1 for d in nononevals if d[0] ==1])
        noWins_d = sum([1 for d in nononevals if d[0] ==1 and d[1] == todaysdistance])
        noRuns_d = sum([1 for d in nononevals if d[1] == todaysdistance and d[0] != 99])
        minFinishTime_d = None
        maxFinishTime_d = None
        medFinishTime_d = None
        #what if none?
   
        allftimes_d= [d[12] for d in nononevals if d[12] !='--' and d[1] == todaysdistance and d[0] != 99]
        if len(allftimes_d) >0:
            minFinishTime_d = min(allftimes_d)
            maxFinishTime_d = max(allftimes_d)
            medFinishTime_d = median(allftimes_d)
        avgsp_d = None
        if noRuns_d >0:
            avgsp_d = (sum([d[9] for d in nononevals if d[9] !='--' and d[1] == todaysdistance])) / noRuns_d
            avgsp_d = round(avgsp_d,3)

        print("CareerWins", noWins)
        print("Wins_d", noWins_d)
        print("Runs_d", noRuns_d)
        print("BestFinishTime_d", minFinishTime_d)
        print("WorstFinishTime_d", maxFinishTime_d)
        print("MedianFinishTime_d", medFinishTime_d)
        print("AvgWinOdds_d", avgsp_d)

        response.meta['horse']['Starts'] = starts
        response.meta['horse']['Scratched'] = allruns-starts
        response.meta['horse']['CareerWins'] = noWins
        response.meta['horse']['Wins_d'] = noWins_d
        response.meta['horse']['Runs_d'] = noRuns_d
        response.meta['horse']['WinSR_d'] = getSR(noWins_d, noRuns_d)
        response.meta['horse']['BestFinishTime_d'] = minFinishTime_d
        response.meta['horse']['AvgWinOdds_d'] = avgsp_d


        h_distance = row.xpath("td")[4].xpath("text()").extract()
        pastdistances.extend(h_distance)
        h_raceconfigs = row.xpath("td")[3].xpath("/text()").extract()
        pastraceconfigs.extend(h_raceconfigs)
        # 20/01/16

        # h_places = row.xpath("td")[1].xpath("*//text()").extract()[0].strip()
        # h_racedates = datetime.strptime(row.xpath("td")[2].xpath("text()").extract()[0].strip(),"%d/%m/%y")
        # print("pastplaces", h_places)
        # print("pastdate", h_racedate)

        #GET COURSE STATS? CDWINS CWINS CLWINS-RUNS CDWINSR DATSINCELAST RUN LTOJ LTOT LTODCHANGE ISLSW? Trainerchange pastrainers
        # ZIP KLISTSDaysSinceLastRun


        # pastraceindexes= filter(lambda x: x.strip(), pastraceindexes)
        # print("should be equal", maxi+1, len(pastraceindexes)) #filter based on max race depth
        # td[not(@width) and not(@height) and contains(@class, 'htable_eng_text')]
        # cleaning lists 1
        # pastraceconfigs_ = filter(lambda x: x.strip(), pastraceconfigs)
        # # pastdistances_ = filter(lambda x: x.strip(), pastdistances)

        # pastracedates_= filter(lambda x: x.strip(), pastracedates)
        # pastracedates = [ datetime.strptime(x, "%d/%m/%y").date() for x in pastracedates_]
        # item['pastraceindexes'] = pastraceindexes

        yield response.meta['horse']

        # except Exception, e:
        #     logger.info("In Horse skipping horse code %s because of error: %s" % (horsecode, str(e)))