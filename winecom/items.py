#-*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst


class WinecomItem(scrapy.Item):
    image = scrapy.Field(output_processor=TakeFirst())
    style = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    item_number = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())
    winery = scrapy.Field(output_processor=TakeFirst())
    winery_location = scrapy.Field(output_processor=TakeFirst())
    abv = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    subname = scrapy.Field(output_processor=TakeFirst())
    collectible = scrapy.Field(output_processor=TakeFirst())
    pro_reviews = scrapy.Field()
    cust_reviews = scrapy.Field()
    vintage = scrapy.Field(output_processor=TakeFirst())
    updated = scrapy.Field(output_processor=TakeFirst())
