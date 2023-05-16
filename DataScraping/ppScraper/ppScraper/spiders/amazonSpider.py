import scrapy
from urllib.parse import urljoin
import re

class AmazonSpider(scrapy.Spider):
    name = 'amazonSpider'
    allowed_domains = ['amazon.ca']
    start_urls = ['http://amazon.ca/']

    def start_requests(self):
        search_items = ['mouse']
        for item in search_items:
            search_url = f'https://www.amazon.ca/s?k={item}&page=1'
            yield scrapy.Request(url=search_url, callback=self.parse, meta={'item': item, 'page': 1})
    
    def parse(self, response):
        products = response.css('.s-result-item')

        for product in products:
            product_link = product.css('h2 a::attr(href)').get()
            if product_link is not None:
                yield response.follow(product_link, self.parse_product)
                break

        # next_page = response.css('.s-pagination-container a::attr(href)').get()
        # if next_page:
        #     yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        title = response.css('#productTitle::text').get().strip()
        price = response.css('span.a-offscreen::text').get().strip()
        brand = response.css('span.po-break-word::text').get().strip()
        category = response.css('#nav-subnav').attrib['data-category']
        category_display = response.css('span.nav-a-content::text').get()
        description = response.css('#feature-bullets ul li ::text').getall()
        description = ''.join([x for x in description])

        yield {
            'title': title,
            'price': price,
            'brand': brand,
            'category': category,
            'category_display': category_display,
            'description': description
        }