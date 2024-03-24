import src.app.database as _database

# Create tables
def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)