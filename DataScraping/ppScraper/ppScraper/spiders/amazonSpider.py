import scrapy
class AmazonSpider(scrapy.Spider):
    name = 'amazonSpider'
    allowed_domains = ['amazon.ca']
    start_urls = ['http://amazon.ca/']

    def start_requests(self):
        # search_items = ['mouse', 'watch']
        search_items = ['watch']
        for item in search_items:
            search_url = f'https://www.amazon.ca/s?k={item}'
            yield scrapy.Request(url=search_url, callback=self.parse)
    
    def parse(self, response):
        products = response.css('.s-result-item')

        for cnt, product in enumerate(products):
            product_link = product.css('h2 a::attr(href)').get()
            if product_link is not None:
                yield response.follow(product_link, self.parse_product)

        next_page = response.css('.s-pagination-container a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        try:
            title = response.css('#productTitle::text').get().strip()
        except AttributeError:
            title = ""

        try:
            price = response.css('span.a-offscreen::text').get().strip()
        except AttributeError:
            price = "" 

        try:
            brand = response.css('span.po-break-word::text').get().strip()
        except AttributeError:
            brand = ""

        try:
            manufacturer = response.css('#prodDetails th:contains("Manufacturer") + td.a-size-base.prodDetAttrValue::text').get()
        except AttributeError:
            manufacturer = "" 

        try:
            category = response.css('#nav-subnav').attrib['data-category']
        except AttributeError:
            category = ""
        
        try:
            category_display = response.css('span.nav-a-content::text').get().replace('\n', '')
        except AttributeError:
            category_display = ""

        try:
            description = response.css('#feature-bullets ul li ::text').getall()
            description = ''.join([x for x in description])
        except AttributeError:
            description = ""

        yield {
            'title': title,
            'price': price,
            'brand': brand,
            'manufacturer': manufacturer,
            'category': category,
            'category_display': category_display,
            'description': description
        }