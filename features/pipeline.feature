Feature: TikaParser pipeline
    
    Scenario: parse an item using Tika server
        Given an instance of TikaParser pipeline, a Raw item and a CmslSpider
        When the process_item is called with a Raw item and a CmslSpider
        Then it should return a Metadata item