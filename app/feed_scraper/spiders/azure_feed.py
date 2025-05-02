import scrapy
import xmltodict

class AzureFeedSpider(scrapy.Spider):
    name = "azure-feed"
    allowed_domains = ["devblogs.microsoft.com"]
    start_urls = ["https://devblogs.microsoft.com/devops/feed/"]

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
