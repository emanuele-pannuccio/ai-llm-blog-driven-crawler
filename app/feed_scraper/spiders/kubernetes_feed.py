import scrapy
import xmltodict

class KubernetesFeedSpider(scrapy.Spider):
    name = "kubernetes-feed"
    allowed_domains = ["kubernetes.io"]
    start_urls = ["https://kubernetes.io/feed.xml"]

    def parse(self, response):
        items = xmltodict.parse(response.text)["rss"]["channel"]["item"]
        for item in items:
            item = {
                "title" : item["title"],
                "link" : item["link"],
                "content" : item["description"],
                "category" : [],
                "source" : response.url
            }
            yield item
            
        print(items)

