import scrapy
from scrapy.utils.sitemap import Sitemap
from scrapy.http import Request, XmlResponse
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.selector import Selector
from winecom.items import WinecomItem
import datetime
import re


class WineSpider(scrapy.spiders.SitemapSpider):
    name = 'wine.com'
    sitemap_urls = ['http://wine.com/sitemap.xml']
    sitemap_rules = [('/.*Detail.aspx/', 'parse_wine')]
    sitemap_alternate_links = True

    def parse_wine(self, response):
        self.logger.info("Loading item...")
        l = ItemLoader(item=WinecomItem(), response=response)
        sel = Selector(response)

        l.add_xpath('image', '//section[1]//img/@src')
        l.add_xpath('style', '/html/body/main/section[2]/ul[1]/li[2]/text()')
        l.add_xpath('price', '/html/body/main/section[2]/div[1]/div[1]/div/span/text()/text()')

        # extract item number
        item_number = sel.xpath('/html/body/main/section[2]/aside/div/text()').re_first('\d+')
        l.add_value('item_number', item_number)

        l.add_xpath('description', '/html/body/main/section[3]/ul[2]/li[1]/section[1]/p/text()')
        l.add_xpath('winery', '/html/body/main/section[3]/ul[2]/li[2]/h3/text()')
        l.add_xpath('winery_location', '/html/body/main/section[3]/ul[2]/li[2]/article/figure/@data-map-geo')

        # extract item number
        l.add_css('abv', 'body > main > section.productAbstract > ul.product-icons > li.abv::text')
        abv  = sel.css('body > main > section.productAbstract > ul.product-icons > li.abv::text')
        abv = abv.re_first('\d+(\.\d{1,2})?')
        l.add_value('abv', abv)


        l.add_value('item_number', item_number)

        # extract name and vintage 
        name = sel.xpath('/html/body/main/section[2]/h1/text()').extract()
        l.add_value('name', name)
        vintage = re.findall('[12]{1}\d{3}', str(name))
        l.add_value('vintage', vintage)


        l.add_xpath('subname', '/html/body/main/section[2]/h2/text()')
        l.add_xpath('collectible', '/html/body/main/section[2]/ul[1]/li[4]//text()')
        l.add_css('pro_reviews', 'Section.criticalAcclaim > ul > li.wineRating')
        l.add_value('updated', str(datetime.datetime.now()))
        return l.load_item()
    
    def parse(self, response):
        pass

    def _parse_sitemap(self, response):
        # Wine.com sitemap does not follow standard (url in loc)
        # rewrote parse to pull url from loc
        if response.url.endswith('/robots.txt'):
            for url in sitemap_urls_from_robots(response.text):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = response.body
            if body is None:
                logger.warning("Ignoring invalid sitemap: %(response)s",
                               {'response': response}, extra={'spider': self})
                return

            s = Sitemap(body)
            loc_reg = '<loc>(.*?)<\/loc>'
            if s.type == 'sitemapindex':
                for loc in re.findall(loc_reg, body.decode('utf-8')):
                    print(loc)
                    yield Request(loc, callback=self._parse_sitemap)
            elif s.type == 'urlset':
                for loc in re.findall(loc_reg, body.decode('utf-8')):
                    yield Request(loc, callback=self.parse_wine)
        
def iter(it, search):
    for d in it:
        yield d[search]

