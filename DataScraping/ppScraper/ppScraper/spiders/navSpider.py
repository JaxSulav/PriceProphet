import scrapy
import csv
import re
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options



class NavSpider(scrapy.Spider):
    name = "navSpider"
    allowed_domains = ["thebay.com"]
    start_urls = ["https://thebay.com"]
    nav_links = list()
    options = Options()
    options.headless = True
    data = []
    file = open("gg.csv", 'a', newline='')
    error_file = open("error_urls.csv", 'a', newline='')
    writer = csv.writer(file)
    error_writer = csv.writer(error_file)
    
    def __init__(self):
        self.driver = webdriver.Firefox(options=self.options)
        # self.driver = webdriver.Chrome('/Users/jaxxsulav/chromedriver_mac64/chromedriver')

    def closed(self, reason):
        self.driver.quit()
        self.file.close()
        self.error_file.close()

    def filter_details(self, data):
        clean = re.compile('<.*?>')
        html_tags_removed = re.sub(clean, '', data)
        return html_tags_removed.replace("\n", "").replace("Details", "")

    def start_requests(self):
        bay_url = "https://www.thebay.com/"
        yield scrapy.Request(url=bay_url, callback=self.parse)
    
    def parse(self, response):
        self.driver.get(response.url)
        element = self.driver.find_element(By.CSS_SELECTOR, 'li.nav-item:nth-child(5)')
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

        # # Wait for the dropdown to appear (adjust the timeout as needed)
        wait = WebDriverWait(self.driver, 10)
        dropdown_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.show'))) #By this point, the only ul.show will be the one for what navbar element we see. So it's okay to select ul.show

        dropdown_links = dropdown_element.find_elements( By.CSS_SELECTOR, "a.dropdown-link")
        # yield scrapy.Request(url=dropdown_links[0].get_attribute('href'), callback=self.parse_subnav, meta={'playwright': True})
        for cnt, link in enumerate(dropdown_links):
            link_href = link.get_attribute('href')
            yield scrapy.Request(url=link_href, callback=self.parse_subnav, meta={'playwright': True})

    def parse_subnav(self, response):
        # gg = response.css('div.pdp-link')
        # print("SSSSSS: ", gg[0].css('a::attr(href)').get())
        products = response.css('div.pdp-link')
        if products:
            for product in products:
                url = product.css('a::attr(href)').get()
                # scrape_url = self.get_scrapeops_url(url)
                yield response.follow(url, self.parse_product)
        else:
            print("ERROR IN LINK ", response.request.url)
            yield None

    def parse_product(self, response):
        title = price = brand = description = category = ""
        try:
            print("Product Url, ", response.request.url)
            title = response.css('.product-name::text').get()
            price = response.css('span.formatted_sale_price::text').get()
            brand = response.css('a.product-brand::text').get().replace("\n", "")
            description = self.filter_details(response.css('div.collapsible-xl').get().split('<br>')[0].strip())
            category_list = response.css('div.product-breadcrumb a::text').getall()
            ordered_category_list = list(OrderedDict.fromkeys(category_list))[:-1]
            category = "/".join(ordered_category_list).strip().replace("\n", "").replace(" ", "")
        except Exception as e:
            self.error_writer.writerow([response.request.url])
            print("ERROR in PRODUCT: ", response.request.url, ":::: ", str(e))

        print(
            "INFO: ", title,price,brand,description,category
        )
        self.writer.writerow([title, price, brand, description, category])


        yield {
            "title": title,
            "price": price,
            "brand": brand,
            "description": description,
            "category": category
        }


