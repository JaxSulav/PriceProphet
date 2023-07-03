# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from .logger import setup_logger
import logging
import random

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class PpscraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class PpscraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScraperAPIMiddleware(object):
    def __init__(self):
        self.api_keys = []
        self.tested_apis = []
        with open('./scraperapis.txt', 'r') as f:
            for line in f:
                try:
                    self.api_keys.append(str(line).replace("\n", "").strip())
                except ValueError:
                    pass

        self.elog = setup_logger("middlewareError", 'middleware.log', level=logging.DEBUG)
        self.api_url = "http://scraperapi:idk@proxy-server.scraperapi.com:8001"
        

    def process_request(self, request, spider):
        proxy = self.api_url
        request.meta['proxy'] = proxy

    def process_response(self, request, response, spider):
        # We take a random key
        # attach to url
        # re-request 5 times if failed
        # leave as it is if not failed
        if len(self.tested_apis) == len(self.api_keys):
            self.tested_apis = []
        if response.status != 200:
            num_retries = request.meta.get('retry_x', 0) + 1
            if num_retries <= 5:
                if self.api_keys:
                    request_clone = request.copy()
                    index = random.choice([i for i in range(len(self.api_keys)) if i not in self.tested_apis])
                    api_key = self.api_keys[index]
                    self.api_url = f"http://scraperapi:{str(api_key)}@proxy-server.scraperapi.com:8001"
                    self.elog.info(f"Scraper API KEY CHANGED TO: {api_key}")
                    self.tested_apis.append(index)
                    request.meta['proxy'] = self.api_url
                    request_clone.meta['retry_x'] = num_retries
                    request_clone.dont_filter = True  
                    return request_clone
                
        return response