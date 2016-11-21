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
        if 'detail' not in response.url.lower(): return
        l = ItemLoader(item=WinecomItem(), response=response)
        sel = Selector(response)

        l.add_xpath('image', '//section[1]//img/@src')
        #l.add_xpath('style', '/html/body/main/section[2]/ul[1]/li[2]/text()')
        l.add_css('style', 'section .wine-style::text')
        l.add_xpath('price', '/html/body/main/section[2]/div[1]/div[1]/div/span/text()/text()')

        # extract item number
        item_number = sel.xpath('/html/body/main/section[2]/aside/div/text()').re_first('\d+')
        l.add_value('item_number', item_number)

        l.add_xpath('description', '/html/body/main/section[3]/ul[2]/li[1]/section[1]/p/text()')
        l.add_xpath('winery', '/html/body/main/section[3]/ul[2]/li[2]/h3/text()')
        l.add_xpath('winery_location', '/html/body/main/section[3]/ul[2]/li[2]/article/figure/@data-map-geo')

        # extract item number
        abv  = sel.css('body > main > section.productAbstract > ul.product-icons > li.abv::text').extract()
        l.add_value('abv', abv)


        l.add_value('item_number', item_number)

        # extract name and vintage 
        name = sel.xpath('/html/body/main/section[2]/h1/text()').extract()
        l.add_value('name', name)
        vintage = re.findall('[12]{1}\d{3}', str(name))
        l.add_value('vintage', vintage)


        subname = sel.xpath('/html/body/main/section[2]/h2/text()').extract_first().strip()
        #l.add_xpath('subname', '/html/body/main/section[2]/h2/text()')
        l.add_value('subname', subname)
        l.add_xpath('collectible', '/html/body/main/section[2]/ul[1]/li[4]//text()')
        # extract all proreview elements (reviewer, ratingProvider, reviewText, ratingScore)
        keys = ['reviewer', 'rating_provider', 'score', 'rating_text']

        review_sel = sel.css('Section.criticalAcclaim > ul > li.wineRating')
        reviewers = [elem.css('.reviewer::text').extract_first() for elem in review_sel]
        rating_providers = [elem.css('.ratingProvider::text').extract_first()  for elem in review_sel]
        rating_scores = [elem.css('.ratingScore::text').extract_first() for elem in review_sel]
        review_texts = [elem.css('.reviewText::text').extract_first() for elem in review_sel]
        reviews = zip(reviewers, rating_providers, rating_scores, review_texts)
        # create dictionary of reviews for better json mapping
        dicts = []
        for review in reviews:
            dicts.append(dict(zip(keys,review)))
        l.add_value('pro_reviews', dicts)

        # Extract customer reviews
        # include rating, rating text (if present), date, location, and username
        cust_rev_sel = sel.css('.topReviews > article')
        def extract_custinfo(cust_record):
            elements = ['.reviewText', '.starRatingText', '.reviewDate',\
                    '.reviewAuthorAlias', '.reviewAuthorLocation']
            keys = ['review_text', 'rating', 'date', 'author', 'author_location']
            extracted_elements = [cust_record.css(element +'::text').extract_first()\
                    for element in elements]
            # Clean up whitespacing
            extracted_elements = list(map(lambda x: x.strip(), extracted_elements))
            # if there is no author text don't include it
            if extracted_elements[0] == '':
                extracted_elements = extracted_elements[1:]
                keys = keys[1:]

            return dict(zip(keys, extracted_elements))
        cust_reviews = [extract_custinfo(record) for record in cust_rev_sel]
        l.add_value('cust_reviews', cust_reviews)


        l.add_value('updated', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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

