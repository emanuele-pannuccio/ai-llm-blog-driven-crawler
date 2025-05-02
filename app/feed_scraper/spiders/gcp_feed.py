import scrapy
import xmltodict
class GcpFeedSpider(scrapy.Spider):
    name = "gcp"
    allowed_domains = ["cloudblog.withgoogle.com"]
    start_urls = ["https://cloudblog.withgoogle.com/rss"]

    def parse(self, response):
        items = xmltodict.parse(response.text)["rss"]["channel"]["item"]
        for item in items:
            item = {
                "title" : item["title"],
                "link" : item["link"],
                "content" : item["description"],
                "category" : item["category"],
                "source" : response.url
            }
            yield item
            
        print(items)
