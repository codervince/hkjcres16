##todos

27th JAN 2016

1. Make each row from results table an individual horseitem (zip fields one field per runner)
2. Take each row and add fields from sectional_time_url to each runner
3. Return as single item or combine with Hkjcres16Item and write to CSV/JSON/HD5
   (any pandas-comparible IO format)[http://pandas.pydata.org/pandas-docs/stable/io.html]

____________

Here's some code from an earlier version (in this case all the fields weer combined into a single item)

  logger.info("This is meta_Dict in parse race {}".format(meta_dict))
        request.meta.update(meta_dict)
        yield request


 def parse_sectional_time(self, response):      
        '''
        horsenumber, horsename, horsecode
        marginsbehindleader = db.Column(postgresql.ARRAY(Float)) #floats
        sec_timelist= db.Column(postgresql.ARRAY(Float))
        '''
        horse_lines_selector = response.xpath('//table[@class="bigborder"]//table//a/../../..')
        sectional_time_selector = response.xpath('//table[@class='
        '"bigborder"]//table//a/../../../following-sibling::tr[1]')
        for line_selector, time_selector in zip(horse_lines_selector,sectional_time_selector):
           
            horsecode = horse_name_dict['code']
           
            sec_timelist = [time.strip() for time in time_selector.xpath('td/text()').extract()]
            sec_timelist_len = len(sec_timelist)
            sec_timelist.extend([None for i in xrange(6-sec_timelist_len)])
            sec_timelist = map(get_sec_in_secs, sec_timelist)
            
            marginsbehindleader = [s.strip('\t\n\r ') for s in line_selector.xpath('td//table//td/text()').extract()]
            marginsbehindleader.extend([None]*(6 - len(marginsbehindleader)))
            marginsbehindleader = map(horselengthprocessor, marginsbehindleader)


    NEW ITEMS
         sec_timelist []
         marginsbehindleader = []
        matched to horse
            


LATER
            IMPORT RECORD STANDARD TIMES SEPARATELY
            horsespeedrating= horsespeedrating,
            stdtime= response.meta['stdtime'],
            recordtime= response.meta['recordtime'],
            recordtimeperlength= response.meta['recordtimeperlength'],
            thistrainerentries (trainerpreference)
            


