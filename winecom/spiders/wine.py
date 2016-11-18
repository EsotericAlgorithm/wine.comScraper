import scrapy
from scrapy.utils.sitemap import Sitemap
from scrapy.http import Request, XmlResponse
import re

class WineSpider(scrapy.spiders.SitemapSpider):
    name = 'wine.com'
    sitemap_urls = ['http://wine.com/sitemap.xml']
    sitemap_rules = [('/.*Detail.aspx/', 'parse_wine')]
    sitemap_alternate_links = True

    def parse_wine(self, response):
        print(response.title)
    
    def parse(self, response):
        pass

    def _parse_sitemap(self, response):
        self.logger.info("Custom sitemap parsing function initiating")
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

