import scrapy
import xmltodict

class CisaSpider(scrapy.Spider):
    name = "cisa"
    allowed_domains = ["www.cisa.gov"]
    start_urls = ["https://www.cisa.gov/cybersecurity-advisories/cybersecurity-advisories.xml"]

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
            
