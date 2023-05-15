import scrapy


class AmazonSpider(scrapy.Spider):
    name = 'amazonSpider'
    allowed_domains = ['amazon.ca']
    start_urls = ['http://amazon.ca/']

    def parse(self, response):
        pass
