Feature: CmslSpider

    Scenario: CmslSpider should be able to parse a response into an item
        Given a webcrawler.spiders.cmsl.CmslSpider and a scrapy.http.Response
        When parse_item method of CmslSpider is invoked with a response
        Then it should return a webcrawler.items.Item
    
    Scenario: CmslSpider.extract_external_links should extract only external links
        Given a webcrawler.spiders.cmsl.CmslSpider and a scrapy.http.Response
        When extract_external_links is invoked with a response
        Then it should return a list of urls
        Then the urls should be external urls