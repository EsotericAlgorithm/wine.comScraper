# Wine.com Scraper
A scraper to crawl and scrape product information from wine.com. Requires [scrapy](https://scrapy.org/). 

## Running Scraper
> scrapy crawl wine.com --set FEED_URI=output.json --set FEED_FORMAT=json

##TODO  
* Correctly scrape price (does not account for sale price)
* Use SQLAlchemy to load into sqlite database

