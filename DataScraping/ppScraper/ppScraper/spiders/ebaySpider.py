import scrapy
import json
import re
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
import mysql.connector
from ..logger import setup_logger
import logging
from urllib.parse import urlparse
from .helper import get_parsed_url

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
        self.cursor.execute("CREATE TABLE IF NOT EXISTS page_links (id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255) UNIQUE, name VARCHAR(255) NULL, url_txt TEXT NULL)")
        print("PageLinks table created....")

    def create_scraped_urls_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_links (
                id INT AUTO_INCREMENT PRIMARY KEY,
                url VARCHAR(255) UNIQUE,
                url_full TEXT NULL,
                name VARCHAR(500) NULL,
                price VARCHAR(32) NULL,
                item_condition VARCHAR(255) NULL,
                shipping VARCHAR(255) NULL,
                located_in VARCHAR(255) NULL,
                last_price VARCHAR(32) NULL,
                us_price VARCHAR(32) NULL,
                return_policy VARCHAR(255) NULL,
                description_url TEXT NULL,
                category VARCHAR(255) NULL,
                authenticity VARCHAR(128) NULL,
                money_back VARCHAR(128) NULL,
                seller_positive_feedback VARCHAR(128) NULL,
                seller_feedback_comments TEXT NULL,
                seller_item_sold VARCHAR(32) NULL,
                seller_all_feedback_url TEXT NULL,
                trending VARCHAR(24) NULL,
                stock VARCHAR(255) NULL,
                brand VARCHAR(255) NULL,
                watchers VARCHAR(24) NULL
            )
        """)
    
    def create_urls_scrape_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS scrape_links(id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(255) UNIQUE, name VARCHAR(255) NULL, url_txt TEXT NULL)")

    
    def is_url_scraped(self, url):
        self.cursor.execute("SELECT url FROM scraped_urls WHERE url = %s", (url,))
        if self.cursor.fetchone() is not None:
            return True
        return False
    
    def insert_page_link(self, url, name):
        self.cursor.execute("INSERT IGNORE INTO page_links (url, name, url_txt) VALUES (%s, %s, %s)", (url, name, url))
        self.conn.commit()
    
    def insert_product_link(self, url, url_full):
        self.cursor.execute("INSERT IGNORE INTO scrape_links (url, url_txt) VALUES (%s, %s)", (url, url_full,))
        self.conn.commit()
        print(f"inserted into db {url}")
    
    def insert_scraped_data(self, data):
        try:
            self.cursor.execute("""
                INSERT IGNORE INTO scraped_links (
                    url, url_full, name, price, item_condition, shipping, located_in, last_price, us_price, 
                    return_policy, description_url, category, authenticity, money_back, seller_positive_feedback, 
                    seller_feedback_comments, seller_item_sold, seller_all_feedback_url, trending, stock, brand, watchers
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['url'], data['url_full'], data['name'], data['price'], data['item_condition'], data['shipping'],
                data['located_in'], data['last_price'], data['us_price'], data['return_policy'], data['description_url'],
                data['category'], data['authenticity'], data['money_back'], data['seller_positive_feedback'],
                data['seller_feedback_comments'], data['seller_item_sold'], data['seller_all_feedback_url'],
                data['trending'], data['stock'], data['brand'], data['watchers']))
            self.conn.commit()

        except Exception as e:
            print(f"Error occurred: {e}")
            self.conn.rollback()
    
    def get_urls_to_scrape(self):
        self.cursor.execute("""SELECT url FROM scrape_links""")
        return self.cursor.fetchall()
    
    def get_scraped_links(self):
        self.cursor.execute("""SELECT url FROM scraped_links""")
        return self.cursor.fetchall()

    def get_page_links(self):
        self.cursor.execute("""SELECT url FROM page_links""")
        return self.cursor.fetchall()

    def close_connection(self):
        self.conn.close()
        self.cursor.close()


class EbayNavSpider(scrapy.Spider):
    """
        Goes through nav links in navbar.
        Done manually for each link in navbar
    """
    name = "ebayNavSpider"
    allowed_domains = ["ebay.ca"]
    options = Options()

    start_urls = ["https://ebay.ca"]
    
    def __init__(self):
        self.driver = webdriver.Firefox(options=self.options)
        
    def closed(self, reason):
        self.driver.quit()
        self.db.close_connection()

    def start_requests(self):
        self.db = DBMgmt("localhost", "root", "password", "PriceProphet")
        self.db.create_page_links_table()
        self.db.create_scraped_urls_table()
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
    
    def men_accessories(self, response):
        self.db.insert_page_link(response.request.url, "Men's Accessories")
        links = response.css('#s0-27-9-0-1[0]-0-1[0]-0-12-list li a::attr(href)').getall()
        for link in links:
            self.db.insert_page_link(link, "Men's Accessories")
            

    # def process_nav_items_fashion(self, links):
        # yield scrapy.Request(links[0].get_attribute("href"), self.womens_clothing)
        # yield scrapy.Request(links[1].get_attribute("href"), self.women_shoes)

    def parse(self, response):
        self.driver.get(response.url)
        fashion_element = self.driver.find_element(By.CSS_SELECTOR, '#mainContent > div.hl-cat-nav > ul > li:nth-child(8)')
        hover = ActionChains(self.driver).move_to_element(fashion_element)
        hover.perform()

        wait = WebDriverWait(self.driver, 10)
        dropdown_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li.hl-cat-nav__js-show')))
        dropdown_links = dropdown_element.find_elements(By.CSS_SELECTOR, "a.hl-cat-nav__js-link")

        yield scrapy.Request(dropdown_links[0].get_attribute("href"), self.women_clothing)
        yield scrapy.Request(dropdown_links[1].get_attribute("href"), self.women_shoes)
        yield scrapy.Request(dropdown_links[2].get_attribute("href"), self.men_clothing)
        yield scrapy.Request(dropdown_links[3].get_attribute("href"), self.men_shoes)


class EbayProductSpider(scrapy.Spider):
    """
        Goes through every product link and extract attributes from each page
    """
    name = "ebayProductSpider"
    allowed_domains = ["ebay.ca"]

    start_urls = ["https://ebay.ca"]
    
    def __init__(self):
        # Scrapy has it's own logger, we are using our custom logger here, elog
        self.elog = setup_logger(self.name, 'eBayProductspider.log', level=logging.DEBUG)
        self.countlog = setup_logger(self.name, 'CountProducts.log', level=logging.DEBUG)
    
    def closed(self, reason):
        self.db.close_connection()

    def start_requests(self):
        self.db = DBMgmt("localhost", "root", "password", "PriceProphet")
        # self.db.create_scraped_urls_table()
        prods = self.db.get_urls_to_scrape()
        scraped_raw = self.db.get_scraped_links()
        scraped = set(x[0] for x in scraped_raw)

        for cnt, page in enumerate(prods):
            # if cnt > 4500:
            #     break
            url = str(page[0])
            self.countlog.info(f"Url: {url}")
            self.countlog.info(f"Cnt: {cnt}")
            if url in scraped:
                self.elog.info(f"Url already scraped: {url}")
                continue
            yield scrapy.Request(url=url, callback=self.parse)
        # yield scrapy.Request(url="https://www.ebay.ca/itm/364309946358", callback=self.parse)
        # yield scrapy.Request(url="https://www.ebay.ca/itm/285228327185", callback=self.parse)

    def parse(self, response):
        us_price = price = ""
        url = get_parsed_url(response.request.url)
        url_full = response.request.url

        try:
            name = response.css("h1.x-item-title__mainTitle span::text").get()
        except Exception as e:
            name = ""
            self.elog.error(f"Error occurred while extracting element: {e}")

        try:
            condition = response.css("div.x-item-condition-value span.ux-textspans::text").get()
        except Exception as e:
            condition = ""
            self.elog.error(f"Error occurred while extracting element: {e}")
        
        try:
            prices = list()
            prices.append(response.css(".x-price-primary span.ux-textspans::text").get())
            prices.append(response.css(".x-price-approx__price > span:nth-child(1)::text").get())
            for p in prices:
                if p is None:
                    continue
                if "U" in p:
                    us_price = p
                else:
                    price = p
        except Exception as e:
            self.elog.error(f"Error occurred while extracting element: {e}") 
        
        try:
            last_price = response.css(".x-additional-info__textual-display span.ux-textspans--STRIKETHROUGH::text").get()
            if not last_price:
                last_price = ""
        except Exception as e:
            last_price = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 

        try:           
            shipping_price_secondary = None
            info_div = response.css('div#SRPSection')
            shipping_bold_secondary = info_div.css('div.ux-labels-values-with-hints--SECONDARY-SMALL span.ux-textspans--BOLD::text').getall()
            for item in shipping_bold_secondary:
                if "approx" in item:
                    shipping_price_secondary = item
                    break
            
            if shipping_price_secondary:
                shipping = shipping_price_secondary
            else:
                shipping = "Free"
        except Exception as e:
            shipping = ""
            self.elog.error(f"Error occurred while extracting element: {e}")

        try:
            pre_text = response.css(".d-shipping-minview span.ux-textspans--SECONDARY::text").getall()
            located_in = [x for x in pre_text if "Located in" in x]
            if located_in:
                located_in = located_in[0].replace("Located in:", "").strip()
            else:
                located_in = ""
        except Exception as e:
            located_in = ""
            self.elog.error(f"Error occurred while extracting element: {e}")

        try:
            text = response.css(".ux-layout-section--returns span.ux-textspans::text").getall()
            returns = ' '.join(text).replace("See details", "").replace("Returns:", "").strip()
        except Exception as e:
            returns = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 
        
        try:
            description_url = response.css("iframe#desc_ifr::attr(src)").get()
        except Exception as e:
            description_url = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 

        try:
            texts = response.css('nav.breadcrumbs ul li a.seo-breadcrumb-text span::text').getall()
            cleaned_texts = [text.strip() for text in texts]
            category = '/'.join(cleaned_texts)
        except Exception as e:
            category = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 
        
        try:
            authenticity = ""
            texts = response.css(".ux-section-icon-with-details__data-title span.ux-textspans::text").getall()
            for text in texts:
                if "Authenticity Guarantee" in text:
                    authenticity = "Yes"
                    break
        except Exception as e:
            authenticity = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 
        
        try:
            money_back = "No"
            texts = response.css(".ux-section-icon-with-details__data-title span.ux-textspans::text").getall()
            for text in texts:
                if "Money Back Guarantee" in text:
                    money_back = "Yes"
                    break
        except Exception as e:
            money_back = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 

        try:
            texts = response.css(".ux-seller-section__content span.ux-textspans::text").getall()
            seller_positive_rating = [x for x in texts if "feedback" in x]
            if seller_positive_rating:
                seller_positive_rating = seller_positive_rating[0].strip()
            else:
                seller_positive_rating = ""
        except Exception as e:
            seller_positive_rating = ""
            self.elog.error(f"Error occurred while extracting element: {e}")
        
        try:
            seller_all_feedback_url = response.css(".fdbk-detail-list__btn-container__btn::attr(href)").get()
        except Exception as e:
            seller_all_feedback_url = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 
        
        try:
            seller_feedback_comments = json.dumps(response.css(".d-stores-info-categories__details-container__tabbed-list div.fdbk-container__details__comment span::text").getall())
            # json.loads(list_name)
        except Exception as e:
            seller_feedback_comments = json.dumps([])
            self.elog.error(f"Error occurred while extracting element: {e}") 

        try:
            trending = "No"
            texts = response.css(".x-wtb-signals span.ux-textspans::text").getall()
            cleaned_texts = [text.strip() for text in texts]
            final = ''.join(cleaned_texts)
            quantity_sold = re.findall(r'\b\d+\b', final)
            if "trending" in final:
                trending = "Yes/"
                if quantity_sold:
                    trending = trending + str(quantity_sold[0])
        except Exception as e:
            trending = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 
        
        try:
            texts = response.css(".d-quantity__availability span.ux-textspans::text").getall()
            if texts:
                stock = "".join([text.strip() for text in texts])
            else:
                stock = ""
        except Exception as e:
            stock = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 

        try:
            watchers = ""
            texts = response.css("#why2buy span.w2b-sgl::text").getall()
            if texts:
                for text in texts:
                    if "watcher" in text:
                        watchers = re.findall(r'\b\d+\b', text)
                        if watchers:
                            watchers = watchers[0]
                        break
        except Exception as e:
            watchers = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 
        
        try:
            seller_item_sold = response.css(".d-stores-info-categories__container__info__section__item:nth-child(3) span:nth-child(1)::text").get().strip()
        except Exception as e:
            seller_item_sold = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 

        try:
            brand = response.xpath('//div[@class="ux-layout-section-evo__row"]//span[text()="Brand"]/following::span[@class="ux-textspans"][1]/text()').get()
        except Exception as e:
            brand = ""
            self.elog.error(f"Error occurred while extracting element: {e}") 

        
        data = {
            'url': url,
            'url_full': url_full,
            'name': name,
            'price': price,
            'item_condition': condition,
            'shipping': shipping,
            'located_in': located_in,
            'last_price': last_price,
            'us_price': us_price,
            'return_policy': returns,
            'description_url': description_url,
            'category': category,
            'authenticity': authenticity,
            'money_back': money_back,
            'seller_positive_feedback': seller_positive_rating,
            'seller_feedback_comments': seller_feedback_comments,
            'seller_item_sold': seller_item_sold,
            'seller_all_feedback_url': seller_all_feedback_url,
            'trending': trending,
            'stock': stock,
            'watchers': watchers,
            'brand': brand
        }
        self.db.insert_scraped_data(data)
        # print("DATA:", data)
        # yield data


class EbayPageSpider(scrapy.Spider):
    """
        Goes through each and every links taken from navbar links.
        Goes through x number of pages from the pagination section
        Modify 'pages' to go through x number of pages
    """
    name = "ebayPageSpider"
    allowed_domains = ["ebay.ca"]

    start_urls = ["https://ebay.ca"]
    
    def __init__(self):
        # Scrapy has it's own logger, we are using our custom logger here, elog
        self.elog = setup_logger(self.name, 'eBayProductspider.log', level=logging.DEBUG)
        self.pages = 500

    def closed(self, reason):
        self.db.close_connection()

    def start_requests(self):
        self.db = DBMgmt("localhost", "root", "password", "PriceProphet")
        self.db.create_urls_scrape_table()
        all_pages_from_nav = self.db.get_page_links()
        for page in enumerate(all_pages_from_nav):
            url = str(page[1][0])
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        raw_products = response.css(".b-list__items_nofooter a.s-item__link::attr(href)").getall()
        products_url = [x for x in raw_products]
        for url in products_url:
            self.db.insert_product_link(get_parsed_url(url), url)

        # We are setting a limit here upto x pages per url in scrape urls
        for i in range(self.pages):
            next_page = response.css('a.pagination__next::attr(href)').get()
            if next_page:
                yield response.follow(next_page, self.parse)
            else:
                break


     