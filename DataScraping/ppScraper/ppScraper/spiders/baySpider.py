import scrapy
import csv
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
import re
import time
from datetime import datetime

class BayspiderSpider(scrapy.Spider):
    name = "baySpider"
    allowed_domains = ["thebay.com"]
    start_urls = ["https://thebay.com"]
    nav_links = list()
    options = Options()
    options.headless = True
    data = []
    file = open("ppScraper/data/all_d.csv", 'a', newline='')
    error_file = open("error_urls.csv", 'a', newline='')
    success_file = open("success_urls.csv", 'a', newline='')
    # writer = csv.writer(file)
    error_writer = csv.writer(error_file)
    success_writer = csv.writer(success_file)

    def __init__(self):
        self.driver = webdriver.Firefox(options=self.options)
        self.driver2 = webdriver.Firefox(options=self.options)
        self.start_point = 8
        self.end_point = 10
        # self.driver = webdriver.Chrome('/Users/jaxxsulav/chromedriver_mac64/chromedriver')

    def closed(self, reason):
        self.driver.quit()
        self.driver2.quit()
        # self.file.close()
        self.error_file.close()
        self.success_file.close()

    def filter_details(self, data):
        clean = re.compile('<.*?>')
        html_tags_removed = re.sub(clean, '', data)
        return html_tags_removed.replace("\n", "").replace("Details", "")

    def start_requests(self):
        bay_url = "https://www.thebay.com/"
        yield scrapy.Request(url=bay_url, callback=self.parse)
    
    def parse(self, response):
        self.driver.get(response.url)
        element = self.driver.find_element(By.CSS_SELECTOR, 'li.nav-item:nth-child(2)')
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

        # # Wait for the dropdown to appear (adjust the timeout as needed)
        wait = WebDriverWait(self.driver, 10)
        dropdown_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.show'))) #By this point, the only ul.show will be the one for what navbar element we see. So it's okay to select ul.show

        dropdown_links = dropdown_element.find_elements( By.CSS_SELECTOR, "a.dropdown-link")
        # link_href = dropdown_links[1].get_attribute('href')
        for cnt, link in enumerate(dropdown_links):
            if self.start_point < cnt < self.end_point:
                link_href = link.get_attribute('href')
            
                self.driver2.get(link_href)
                load_more_element = self.driver2.find_elements(By.CLASS_NAME, "ais-InfiniteHits-loadMore")
                if not load_more_element:
                    print(f"Did not scrape {link_href}, because of no load more button")
                    continue
                
                cnt = 0
                while True:
                    if cnt > 46:
                        break
                    cnt += 1
                    try:
                        load_more_button = WebDriverWait(self.driver2, 30).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "ais-InfiniteHits-loadMore"))
                        )
                        time.sleep(2)
                        load_more_button.click()
                    except:
                        break
                
                h3_tags = self.driver2.find_elements(By.TAG_NAME, "h3")
                print("Number of h3: ", len(h3_tags))
                self.success_writer.writerow([f"{datetime.now()} :: Performing scrape on :: {response.request.url}"])

                for cnt, tag in enumerate(h3_tags):
                    try:
                        product_link = tag.find_element(By.CSS_SELECTOR, "a[href*='/product/show']").get_attribute("href")
                        print(f"Product Link {link_href} : {product_link} :: {cnt}")
                        yield scrapy.Request(url=product_link, callback=self.parse_product)
                    except Exception as e:
                        print(f"Exception: error in the link: {link_href}")
            else:
                if cnt > self.end_point:
                    break
                continue
            


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
        # self.writer.writerow([title, price, brand, description, category])

        yield {
            "title": title,
            "price": price,
            "brand": brand,
            "description": description,
            "category": category
        }

