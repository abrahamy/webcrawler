from scrapy.utils.project import get_project_settings
from webcrawler.items import Document, Search


def before_feature(context, feature):
    '''
    Use the test database for running the tests
    '''
    if feature.name is not 'Database Feature':
        return
    
    settings = get_project_settings()
    test_db_uri = 'postgresext+pool://postgres:secret@localhost:5432/test?max_connections=10&stale_timeout=300'
    settings.set('DATABASE_URI', test_db_uri)


def before_tag(context, tag):
    '''
    Drop all tables in the database before each scenario is checked
    '''
    if tag is not 'database_test':
        return
    
    db = Document._meta.database
    with db.execution_context():
        table_names = [m._meta.db_table for m in (Document, Search)]
        
        cursor = db.get_cursor()
        cursor.execute('DROP TABLE IF EXISTS %s, %s CASCADE', table_names)