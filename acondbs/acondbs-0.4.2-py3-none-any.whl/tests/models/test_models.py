from acondbs.db.sa import sa


##__________________________________________________________________||
def test_table_names(app_empty, snapshot):
    '''test the table names
    '''
    table_names = list(sa.Model.metadata.tables.keys())
    snapshot.assert_match(table_names)

##__________________________________________________________________||
