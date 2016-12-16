Feature: ContentParser
    
    Scenario: should be able to process a valid item correctly
        Given a webcrawler.pipelines.ContentParser, webcrawler.items.Item and a webcrawler.spiders.cmsl.CmslSpider
        When process_item is invoked on ContentParser with Item and CmslSpider
        Then it should return a webcrawler.items.Parsed
    
    Scenario: should be able to handle invalid items properly
        Given a webcrawler.pipelines.ContentParser, an invalid item and a webcrawler.spiders.cmsl.CmslSpider
        When process_item is invoked on ContentParser with the item and CmslSpider
        Then it should return the same item unchanged