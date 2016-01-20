import scrapy
from scrapy.loader import ItemLoader
from hkjcres16.items import Hkjcres16Item
from scrapy.loader.processors import TakeFirst,Compose, MapCompose, Identity, Join
from urlparse import urlparse
from collections import defaultdict,OrderedDict, Counter
#from selenium import webdriver
#from time import sleep
import urllib
import re
import logging


def divprocessor(divlist):
    return divprocessor

def timetofloat(t):
    return float("{0:.2f}".format(float(t)))

class RaceItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    raceindex_in = MapCompose(int)
    racedistance_in = Compose(lambda v: v[0], int)
    finishtime_in = MapCompose(timetofloat)
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

    def __init__(self, racedate, racecoursecode, noraces, *args, **kwargs):
        super(HkjcresSpider, self).__init__(*args, **kwargs)
        self.noraces = int(noraces)
        self.base_url = "http://racing.hkjc.com/racing/Info/Meeting/Results/English/Local/" + racedate + '/'+ racecoursecode + '/'

    def start_requests(self):
        #take initial url and extend to cover all races add to start urls
        #create list then return
        urls = list()
        for i in range(1,self.noraces+1):
            yield scrapy.Request( self.base_url+'{0:01}'.format(i), self.parse)
     
    def parse(self, response):
        logger.info('A response from %s just arrived!', response.url)
        loader = RaceItemLoader(Hkjcres16Item(), response=response)
        item = Hkjcres16Item()      
        
        #basic race information

        # item['url'] = response.url
        loader.add_value('url', response.url)

        raceindex_path = re.compile(r'\((\d+)\)')
        item['raceindex'] = response.selector.xpath('//div[@class="boldFont14 color_white trBgBlue"]//text()').re(r'\((\d+)\)')
        loader.add_value('raceindex', response.selector.xpath('//div[@class="boldFont14 color_white trBgBlue"]//text()').re(r'\((\d+)\)'))
        
        #race details table
        newraceinfo = response.xpath('//table[@class ="tableBorder0 font13"]//*[self::td or self::td/span]//text()').extract()
        raceclass = newraceinfo[0].replace('-', '').strip()
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
            div_info['A1'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A1']/following-sibling::td/text()").extract()
            div_info['A2'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A2']/following-sibling::td/text()").extract()
            div_info['A3'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='A3']/following-sibling::td/text()").extract()
            div_info['JOCKEY CHALLENGE'] = response.xpath("//tr[td/text() = 'Dividend']/following-sibling::tr/td[text()='JOCKEY CHALLENGE']/following-sibling::td/text()").extract()
            # for m2 in markets2:
            #     try:
            #         xpathstr21 = str("//tr[td/text() = 'Dividend']/following-sibling::tr/td[contains(.,")
            #         xpathstr22 = str(")]/following-sibling::td/text()")
            #         win_divs2 =response.xpath(xpathstr21 + "'" + str(m2) + "'" + xpathstr22).extract()
            #         div_info[win_divs2[0]] = [ win_divs2[1],win_divs2[2] ]

            #     except:
            #         div_info[m2] = None
        # print div_info
 
        #WHO WON?
        _winners = div_info['WIN']
        _winninghorsenumbers = []
        _winningdivs = []
        for i,w in enumerate(_winners):
            if i%2 ==0: #odd indices are horsenumber, even odds
            #one winner else DH
                _winninghorsenumbers.append(w)
            if i%2 ==1:
                _winningdivs.append(w)
        ##RUNNERS
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
        return loader.load_item()
