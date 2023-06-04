import playwright
import scrapy
import csv

class HudsonSpider(scrapy.Spider):
    name = "hudsonSpider"
    allowed_domains = ["thebay.com"]
    start_urls = ["https://thebay.com"]

    # def __init__(self):
    #     self.driver = webdriver.Firefox()
        # self.driver = webdriver.Chrome('/Users/jaxxsulav/chromedriver_mac64/chromedriver')

    def read_csv_to_list(self, filename):
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            data = [row[0] for row in reader]
            return data
            
    # def closed(self, reason):
    #     self.driver.quit()

    def start_requests(self):
        bay_urls = self.read_csv_to_list("ppScraper/data/hudson_navs/brands.csv")
        yield scrapy.Request(url=str(bay_urls[0]), callback=self.parse,  meta={'playwright': True})
        # for bay_url in bay_urls:
        #     yield scrapy.Request(url=str(bay_url), callback=self.parse,  meta={'playwright': True})
        
    def parse(self, response):
        product_href = self.start_urls[0] + str(response.css('div.pdp-link')[0].css('a::attr(href)').get())
        print("MKLSKSKS: ", product_href)
        gg = response.css('div.pdp-link')[0].css('a::attr(href)').get()
        print("VVVVVVVVVVV: ", gg)
        yield response.follow(gg, self.parse_product, meta={'playwright': True})
        # for product in response.css('div.pdp-link'):
        #     product_href = self.start_urls[0] + str(product.css('a::attr(href)').get())
        #     print("SSSS: ", product_href)
        #     yield scrapy.Request(product_href, self.parse_product, meta={'playwright': True})
    
    def parse_product(self, response):
        print("sdsdsdsdsdsdsdsdsmdlsmdkmksdmksmdkms")
        print("GGGG: ", response.css('.product-name'))
        # yield {
        #     "title": response.css('h1.product-name')

        # }
        yield None