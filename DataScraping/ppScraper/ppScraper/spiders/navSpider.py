import scrapy
import csv
import re
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options



class NavSpider(scrapy.Spider):
    name = "navSpider"
    allowed_domains = ["thebay.com"]
    start_urls = ["https://thebay.com"]
    nav_links = list()
    options = Options()
    options.headless = True

    def __init__(self):
        self.driver = webdriver.Firefox(options=self.options)
        # self.driver = webdriver.Chrome('/Users/jaxxsulav/chromedriver_mac64/chromedriver')

    def closed(self, reason):
        self.driver.quit()

    def filter_details(self, data):
        clean = re.compile('<.*?>')
        html_tags_removed = re.sub(clean, '', data)
        return html_tags_removed.replace("\n", "").replace("Details", "")

    def start_requests(self):
        bay_url = "https://www.thebay.com/"
        yield scrapy.Request(url=bay_url, callback=self.parse)
    
    def parse(self, response):
        self.driver.get(response.url)
        element = self.driver.find_element(By.CSS_SELECTOR, 'li.nav-item:nth-child(8)')
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

        # # Wait for the dropdown to appear (adjust the timeout as needed)
        wait = WebDriverWait(self.driver, 10)
        dropdown_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.show'))) #By this point, the only ul.show will be the one for what navbar element we see. So it's okay to select ul.show

        dropdown_links = dropdown_element.find_elements( By.CSS_SELECTOR, "a.dropdown-link")
        # yield scrapy.Request(url=dropdown_links[0].get_attribute('href'), callback=self.parse_subnav, meta={'playwright': True})
        for link in dropdown_links:
            link_href = link.get_attribute('href')
            yield scrapy.Request(url=link_href, callback=self.parse_subnav, meta={'playwright': True})

    def parse_subnav(self, response):
        # yield response.follow(response.css('div.pdp-link')[0].css('a::attr(href)').get(), self.parse_product)
        for product in response.css('div.pdp-link'):
            url = product.css('a::attr(href)').get()
            yield response.follow(url, self.parse_product)
    
    

    def parse_product(self, response):
        title = response.css('.product-name::text').get()
        price = response.css('span.formatted_sale_price::text').get()
        brand = response.css('a.product-brand::text').get().replace("\n", "")
        description = self.filter_details(response.css('div.collapsible-xl').get().split('<br>')[0].strip())
        category_list = response.css('div.product-breadcrumb a::text').getall()
        ordered_category_list = list(OrderedDict.fromkeys(category_list))[:-1]
        category = "/".join(ordered_category_list).strip().replace("\n", "").replace(" ", "")

        # print(
        #     "title", title,price,brand,description,category
        # )

        yield {
            "title": title,
            "price": price,
            "brand": brand,
            "description": description,
            "category": category
        }


