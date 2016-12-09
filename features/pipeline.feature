Feature: ContentParser feature
    
    Scenario: parse the content of a response
        Given a CmslSpider and Response
        When CmslSpider.parse_item is called
        Then it should return a Raw item
        Given a ContentParser
        When ContentParser.process_item is called
        Then it should return a CrawlData item