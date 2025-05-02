import scrapy
import xmltodict

class AwsFeedSpider(scrapy.Spider):
    name = "aws-feed"
    allowed_domains = ["aws.amazon.com"]
    start_urls = ["https://aws.amazon.com/blogs/devops/feed/","https://aws.amazon.com/blogs/machine-learning/feed/"]

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
        pass