import scrapy
import xmltodict

class GitlabFeedSpider(scrapy.Spider):
    name = "gitlab-feed"
    allowed_domains = ["about.gitlab.com"]
    start_urls = ["https://about.gitlab.com/atom.xml"]

    def parse(self, response):
        items = xmltodict.parse(response.text)["feed"]["entry"]
        for item in items:
            item = {
                "title" : item["title"]["#text"],
                "link" : item["link"]["@href"],
                "content" : item["content"]["#text"],
                "category" : [],
                "source" : response.url
            }
            
            yield item