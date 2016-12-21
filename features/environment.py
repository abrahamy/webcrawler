from webcrawler.items import Document, Search


def before_tag(context, tag):
    '''
    Drop all tables in the database before each scenario is checked
    '''
    if tag is not 'dbtest':
        return
    
    db = Document._meta.database
    models = [Document, Search]
    db.drop_tables(models, safe=True)