import scrapy
import xmltodict

class DevopsabcsFeedSpider(scrapy.Spider):
    name = "devopsabcs-feed"
    allowed_domains = ["blog.devopsabcs.com"]
    start_urls = ["https://blog.devopsabcs.com/index.php/feed/"]

    def parse(self, response):
        items = xmltodict.parse(response.text)["rss"]["channel"]["item"]
        for item in items:
            item = {
                "title" : item["title"],
                "link" : item["link"],
                "content" : item["content:encoded"],
                "category" : item["category"],
                "source" : response.url
            }
            yield item
