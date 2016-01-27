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
            horsenumber = try_int(line_selector.xpath('td[1]/div/text()').extract()[0].strip())
            horse_name_cell = line_selector.xpath('td[3]/div/a/text()').extract()[0]
            horse_name_regexp = '^(?P<name>[^\(]+)\((?P<code>[^\)]+)\)$'
            horse_name_dict = re.match(horse_name_regexp, horse_name_cell).groupdict()
            horsename = horse_name_dict['name']
            horsecode = horse_name_dict['code']
            horsereport = getHorseReport(response.meta['racingincidentreport'], horsename)
            sec_timelist = [time.strip() for time in time_selector.xpath('td/text()').extract()]
            sec_timelist_len = len(sec_timelist)
            sec_timelist.extend([None for i in xrange(6-sec_timelist_len)])
            sec_timelist = map(get_sec_in_secs, sec_timelist)
            horse_path = line_selector.xpath('td[3]/div/a/@href').extract()[0]
            # horse_url = 'http://www.{domain}/english/racing/{path}&Option=1#htop'.format(domain=self.domain, path=horse_path)
            horse_smartform_url = 'http://racing.hkjc.com/racing/info/horse/smartform/english/{hcode}'.format(hcode=horsecode)
            marginsbehindleader = [s.strip('\t\n\r ') for s in line_selector.xpath('td//table//td/text()').extract()]
            marginsbehindleader.extend([None]*(6 - len(marginsbehindleader)))
            marginsbehindleader = map(horselengthprocessor, marginsbehindleader)

            # request = scrapy.Request(response.meta['results_url'],callback=self.parse_results)
			# meta_dict = response.meta
			# meta_dict.update({
			# 'horsenumber': horsenumber,
			# 'horsename': horsename,
			# 'horsecode': horsecode,
			# 'horsereport': horsereport,
			# 'sec_timelist': sec_timelist,
			# # 'horse_url': horse_url,
			# 'horse_smartform_url': horse_smartform_url,
			# 'marginsbehindleader': marginsbehindleader,
			# })
			# print meta_dict
			# request.meta.update(meta_dict)
			# print meta_dict

			##get data from ordered dict
			#get index from horsecodes
            _hc_idx = None
            winoddsrank = 0.0
            horsenos = response.meta['horsenos'].items()
            scratched_horsenos = [ x for x,y in horsenos if y != 99]
            ##Horsecodes is order of place and code includes scratched
            #need a scratched horsecode 
            for x,y in response.meta['horsecodes'].items():
            	if y == horsecode and horsecode not in scratched_horsenos:
            		_hc_idx, hc = x,y
            if _hc_idx:
            	finishtime = response.meta['finishtimes'][_hc_idx]
            	market_prob = response.meta['market_probs'].get(_hc_idx)
            	jockeycode = response.meta['jockeycodes'][_hc_idx]
            	place = response.meta['places'][_hc_idx]
            	runningpositions = response.meta['runningpositions'][_hc_idx]
            	winodds = response.meta['winodds'][_hc_idx]
            #use index to get finishtime, jockeycode, place, winodds, market_probs
            	for i,x in enumerate(response.meta['winoddsranks'].items()):
            		if x[1] == winodds:
            			winoddsrank = i+1
            #with winoddsrank reverse lookup o winodds

            ##TIMES finishtime is it float? sec_timelist_len
            ##versus recordtime
            hls = gettimeperlength(response.meta['racedistance'], finishtime)
            horsespeedrating =  getmetaspeedrank(hls,response.meta['recordtimeperlength'])


            yield items.SimplehkjcresultsItem(

            racedistance = response.meta['racedistance'],
            raceclass=  response.meta['raceclass'],
            racegoing =  response.meta['racegoing'],
            racesurface = response.meta['racesurface'],
            racenumber= int(self.racenumber),
            horsenumber=horsenumber,
            horsecode=horsecode,
            jockeycode=jockeycode,
            finishtime=finishtime,
            theresults = response.meta['theresults'],
            #runnerslist = response.meta['runnerslist'],
            runningpositions= runningpositions,
            market_prob=market_prob,
            race_total_prob =response.meta['race_total_prob'],
            place=place,
            winoddsrank=winoddsrank,
            horsereport=horsereport,
            sec_timelist = sec_timelist,
            marginsbehindleader= marginsbehindleader,
            racedate=self.racedate,
            racecoursecode=self.racecoursecode,
            # winodds = response.meta['winodds'][horsenumber],
            winodds = winodds,
            racepace =response.meta['racepace'],
            racetrainers = response.meta['racetrainers'],
            winningsecs= response.meta['winningsecs'],
            horsespeedrating= horsespeedrating,
            stdtime= response.meta['stdtime'],
            recordtime= response.meta['recordtime'],
            recordtimeperlength= response.meta['recordtimeperlength'],
            #replace these 3
            A1topfavs_windiv= response.meta['A1topfavs_windiv'],
            A2midpricers_windiv= response.meta['A2midpricers_windiv'],
            A3outsiders_windiv= response.meta['A3outsiders_windiv'],
            winningtrainercode = response.meta['winningtrainercode'],
            winningjockeycode = response.meta['winningjockeycode'],
            favpos= response.meta['favpos'],
            favodds = response.meta['favodds'],
            win_combo_div= response.meta['win_combo_div'],
            place_combo_div= response.meta['place_combo_div'],
            qn_combo_div= response.meta['qn_combo_div'],
            qnp_combo_div= response.meta['qnp_combo_div'],
            tce_combo_div= response.meta['tce_combo_div'],
            trio_combo_div=response.meta['trio_combo_div'],
            f4_combo_div= response.meta['f4_combo_div'],
            qtt_combo_div= response.meta['qtt_combo_div'],
            dbl9_combo_div= response.meta['dbl9_combo_div'],
            dbl8_combo_div= response.meta['dbl8_combo_div'],
            dbl7_combo_div= response.meta['dbl7_combo_div'],
            dbl6_combo_div= response.meta['dbl6_combo_div'],
            dbl5_combo_div=response.meta['dbl5_combo_div'],
            dbl4_combo_div= response.meta['dbl4_combo_div'],
            dbl3_combo_div= response.meta['dbl3_combo_div'],
            dbl2_combo_div= response.meta['dbl2_combo_div'],
            dbl1_combo_div= response.meta['dbl1_combo_div'],
            dbl10_combo_div= response.meta['dbl10_combo_div'],
            dbltrio1_combo_div= response.meta['dbltrio1_combo_div'],
            dbltrio2_combo_div= response.meta['dbltrio2_combo_div'],
            dbltrio3_combo_div= response.meta['dbltrio3_combo_div'],
            tripletriocons_combo_div=response.meta['tripletriocons_combo_div'],
            tripletrio_combo_div=response.meta['tripletrio_combo_div']
            )



