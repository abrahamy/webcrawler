Feature: Database Feature
    In order to store the metadata of crawled items
    I want a database feature for storing the documents
    retrieved from the internet and for storing full text
    search indexes for the documents.

    @dbtest
    Scenario: Store a new Document
        Given that new document has been added
        When we query the Document model with it's id
        Then it should return an instance of Document
    
    @dbtest
    Scenario: Post-Save signal triggers
        Given that a new document has been added
        When we query the Search model with it's id
        Then it should return an instance of Search
    
    