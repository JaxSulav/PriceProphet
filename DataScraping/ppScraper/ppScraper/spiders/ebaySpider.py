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
import mysql.connector


class DBMgmt:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def create_page_links_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS page_links (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255) UNIQUE, name VARCHAR(255), url_txt TEXT)")
        print("PageLinks table created....")

    def create_scraped_urls_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_urls (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(255) UNIQUE,
                name VARCHAR(255),
                url_txt TEXT
            )
        """)
        print("ScrapedUrls table created....")
    
    def is_url_scraped(self, url):
        self.cursor.execute("SELECT url FROM scraped_urls WHERE url = %s", (url,))
        if self.cursor.fetchone() is not None:
            return True
        return False
    
    def insert_page_link(self, url, name):
        self.cursor.execute("INSERT IGNORE INTO page_links (url, name, url_txt) VALUES (%s, %s, %s)", (url, name, url))
        self.conn.commit()
        print(f"Inserted into page_link: {url}, {name}")

    def insert_scraped_url(self, url, name):
        self.cursor.execute("INSERT IGNORE INTO scraped_urls (url, name, url_txt) VALUES (%s, %s, %s)", (url, name, url))
        self.conn.commit()
    
    def close_connection(self):
        self.conn.close()


class EbayNavSpider(scrapy.Spider):
    name = "ebayNavSpider"
    allowed_domains = ["ebay.ca"]
    options = Options()

    start_urls = ["https://ebay.ca"]
    
    def __init__(self):
        self.driver = webdriver.Firefox(options=self.options)
        
    def closed(self, reason):
        self.driver.quit()

    def start_requests(self):
        self.db = DBMgmt("localhost", "root", "password", "PriceProphet")
        # self.db.create_page_links_table()
        # self.db.create_scraped_urls_table()
        bay_url = "https://www.ebay.ca/"
        yield scrapy.Request(url=bay_url, callback=self.parse)
    
    def women_clothing(self, response):
        links = response.css("a.b-visualnav__tile::attr(href)").getall()
        for link in links:
            self.db.insert_page_link(link, "Women's Clothing")
    
    def women_shoes_by_categories(self, response):
       self.db.insert_page_link(response.request.url, "Women's Shoes Main")
       links = response.css("a.b-guidancecard__link:not(.b-guidancecard__link--noimg)::attr(href)").getall() 
       for link in links:
           self.db.insert_page_link(link, "Women's Shoes") 

    def women_shoes(self, response):
        self.db.insert_page_link(response.request.url, "Women's Shoes Main")
        links = response.css("a.b-guidancecard__link:not(.b-guidancecard__link--noimg)::attr(href)").getall()
        for cnt, link in enumerate(links):
            self.db.insert_page_link(link, "Women's Shoes Category")
            if cnt < 2:
                yield response.follow(link, self.women_shoes_by_categories)
    
    def men_clothing(self, response):
        links = response.css("a.b-visualnav__tile::attr(href)").getall()
        for link in links:
            self.db.insert_page_link(link, "Men's Clothing")
    
    def men_shoes_by_categories(self, response):
       self.db.insert_page_link(response.request.url, "Men's Shoes Main")
       links = response.css("a.b-guidancecard__link:not(.b-guidancecard__link--noimg)::attr(href)").getall() 
       for link in links:
           self.db.insert_page_link(link, "Men's Shoes") 
    
    def men_shoes(self, response):
        self.db.insert_page_link(response.request.url, "Men's Shoes Main")
        links = response.css("a.b-guidancecard__link:not(.b-guidancecard__link--noimg)::attr(href)").getall()
        for cnt, link in enumerate(links):
            self.db.insert_page_link(link, "Men's Shoes Category")
            if cnt < 5:
                yield response.follow(link, self.men_shoes_by_categories)
                
    # def process_nav_items_fashion(self, links):
        # yield scrapy.Request(links[0].get_attribute("href"), self.womens_clothing)
        # yield scrapy.Request(links[1].get_attribute("href"), self.women_shoes)

    def parse(self, response):
        self.driver.get(response.url)
        fashion_element = self.driver.find_element(By.CSS_SELECTOR, '#mainContent > div.hl-cat-nav > ul > li:nth-child(3)')
        hover = ActionChains(self.driver).move_to_element(fashion_element)
        hover.perform()

        wait = WebDriverWait(self.driver, 10)
        dropdown_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li.hl-cat-nav__js-show')))
        dropdown_links = dropdown_element.find_elements(By.CSS_SELECTOR, "a.hl-cat-nav__js-link")

        yield scrapy.Request(dropdown_links[0].get_attribute("href"), self.women_clothing)
        yield scrapy.Request(dropdown_links[1].get_attribute("href"), self.women_shoes)
        yield scrapy.Request(dropdown_links[2].get_attribute("href"), self.men_clothing)
        yield scrapy.Request(dropdown_links[3].get_attribute("href"), self.men_shoes)