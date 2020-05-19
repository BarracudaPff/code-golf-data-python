class WikidatacrawlerItem(scrapy.Item):
	rid = scrapy.Field()
	rtype = scrapy.Field()
	rsubtype = scrapy.Field()
	rmention = scrapy.Field()
	chrmention = scrapy.Field()
	link = scrapy.Field()
	pass