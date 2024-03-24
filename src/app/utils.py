from sqlalchemy import inspect
from sqlalchemy.orm import Session

def table_exists(db: Session, table_name):
    inspector = inspect(db.get_bind())
    return table_name in inspector.get_table_names()