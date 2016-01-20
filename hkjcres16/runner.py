import json
import logging

from scrapy.crawler import Crawler
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose, TakeFirst
from scrapy import log, signals, Spider, Item, Field
from scrapy.settings import Settings
from twisted.internet import reactor

logger = logging.getLogger('hkjcres_application')
# define an item class
class HKJCresItem(Item):
    raceindex = Field()
   

# define an item loader with input and output processors
class HKJCresItemLoader(ItemLoader):
    default_input_processor = MapCompose(unicode.strip)
    default_output_processor = TakeFirst()

    raceindex_out = Join()


# define a pipeline
class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('items.jl', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item



class HkjcresSpider(scrapy.Spider):
    name = "hkjcres"
    allowed_domains = ["racing.hkjc.com"]

    def __init__(self, racedate, racecoursecode, *args, **kwargs):
        assert racecoursecode in ['ST', 'HV']
        super(HkjcresSpider, self).__init__(*args, **kwargs)
        self.base_url = "http://racing.hkjc.com/racing/Info/Meeting/Results/English/Local/" + racedate + '/'+ racecoursecode + '/'

    def start_requests(self):
        #take initial url and extend to cover all races add to start urls
        #create list then return
        urls = list()
        for i in range(1,13):
            yield scrapy.Request( self.base_url+'{0:02d}'.format(i), self.parse)
     
    def parse(self, response):
        logger.info('A response from %s just arrived!', response.url)
        raceindex_path = re.compile(r'\((\d+)\)')
        for sel in response.xpath('//div[@class="boldFont14 color_white trBgBlue"]//text()'):
            loader = HKJCresItemLoader(HKJCresItem(), selector=sel, response=response)
            loader.add_xpath('raceindex', 'a/text()')
            # loader.add_xpath('link', 'a/@href')
            # loader.add_xpath('desc', 'text()')
            yield loader.load_item()


# callback fired when the spider is closed
def callback(spider, reason):
    stats = spider.crawler.stats.get_stats()  # collect/log stats?

    # stop the reactor
    reactor.stop()


# instantiate settings and provide a custom configuration
settings = Settings()
settings.set('ITEM_PIPELINES', {
    '__main__.JsonWriterPipeline': 100
})

# instantiate a crawler passing in settings
crawler = Crawler(settings)

# instantiate a spider
spider = HkjcresSpider()

# configure signals
crawler.signals.connect(callback, signal=signals.spider_closed)

# configure and start the crawler
crawler.configure()
crawler.crawl(spider)
crawler.start()

# start logging
log.start()

# start the reactor (blocks execution)
reactor.run()