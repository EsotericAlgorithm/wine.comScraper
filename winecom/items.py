#-*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WinecomItem(scrapy.Item):
    image = scrapy.Field()
    style = scrapy.Field()
    price = scrapy.Field()
    item_number = scrapy.Field()
    description = scrapy.Field()
    winery = scrapy.Field()
    winery_location = scrapy.Field()
    abv = scrapy.Field()
    name = scrapy.Field()
    subname = scrapy.Field()
    collectible = scrapy.Field()
    pro_reviews = scrapy.Field()
    cust_reviews = scrapy.Field()
    vintage = scrapy.Field()
    updated = scrapy.Field()
