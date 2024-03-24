import app.database as _database
from typing import List
import app.schemas as _schemas
import app.models as _models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import pandas as pd
from fastapi.exceptions import HTTPException
from sqlalchemy import text
import avro.schema
import app.utils as _utils
from avro.datafile import DataFileWriter
import json
from avro.io import DatumWriter

# Create tables
def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)

# Database Session
def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add new employees
async def create_employees(
    employees: List[_schemas.EmployeesCreate], db: Session
) -> _schemas.Employees:
    employee_objects = [_models.Employees(**employee.model_dump()) for employee in employees]
    db.add_all(employee_objects)
    db.commit()    
    
    # Refresh each individual object to update its state from the database
    for employee in employee_objects:
        db.refresh(employee)
    
    return [_schemas.Employees.model_validate(employee, from_attributes=True) for employee in employee_objects]

# Batch upload employees
async def upload_csv_to_database(file, db: Session):
    try:
        # Read CSV data into a DataFrame
        df = pd.read_csv(file.file, header=None)
        column_names = ['id', 'name', 'datetime', 'department_id', 'job_id']
        df.columns = column_names
        
        db.begin()
        # Upload data into the database
        df.to_sql("hired_employees", db.get_bind(), if_exists="append", index=False)
        # Commit the transaction
        db.execute(text(f"SELECT setval('hired_employees_id_seq', max(id)) FROM hired_employees;"))
        db.commit()
        return {"message": "Data uploaded successfully"}
        
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="IntegrityError: Duplicate entry")

# Backup selected table  
# Load Avro schema from the selected model
def load_avro_schema(table_name):
    schema_dict: dict = _schemas.Employees.avro_schema()
    return avro.schema.parse(json.dumps(schema_dict))
# Backup
def backup_table_to_avro(db: Session, table_name: str):
    # Check if the table exists
    if not _utils.table_exists(db, table_name):
        raise ValueError("Table not found")
    
    # Parse the Avro schema
    avro_schema = load_avro_schema(table_name)

    # Query the data from PostgreSQL
    sql_query = text(f"SELECT * FROM {table_name};")
    data = db.execute(sql_query).fetchall()

    # Convert the retrieved data to a list of dictionaries
    data_dicts = []
    for row in data:
        row_dict = {}
        for column, value in row._mapping.items():
            # Replace NULL values with None
            if value is None:
                value = None
            row_dict[column] = value
        data_dicts.append(row_dict)

    # Generate a datetime timestamp 
    backup_file_name = f"{table_name}_backup.avro"
    
    # Write Avro data to a file
    with open(backup_file_name, 'wb') as f:
        try:
            writer = DataFileWriter(f, DatumWriter(), avro_schema)
            for record in data_dicts:
                writer.append(record)
        except Exception as e:
            print(f"Error writing Avro data to file: {e}")
        finally:
            writer.close()
    return backup_file_name