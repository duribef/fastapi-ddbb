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
from avro.datafile import DataFileReader
from avro.io import DatumReader

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

# Add new departments
async def create_departments(
    departments: List[_schemas.DepartmentCreate], db: Session
) -> _schemas.Department:
    departments_objects = [_models.Departments(**department.model_dump()) for department in departments]
    db.add_all(departments_objects)
    db.commit()    
    
    # Refresh each individual object to update its state from the database
    for department in departments_objects:
        db.refresh(department)
    
    return [_schemas.Department.model_validate(department, from_attributes=True) for department in departments_objects]

# Add new jobs
async def create_jobs(
    jobs: List[_schemas.JobCreate], db: Session
) -> _schemas.Department:
    jobs_objects = [_models.Jobs(**job.model_dump()) for job in jobs]
    db.add_all(jobs_objects)
    db.commit()    
    
    # Refresh each individual object to update its state from the database
    for job in jobs_objects:
        db.refresh(job)
    
    return [_schemas.Job.model_validate(job, from_attributes=True) for job in jobs_objects]

# Batch upload
async def upload_csv_to_database(file, db: Session):
    table_name = file.filename.replace('.csv','')
    try:
        # Get column names
        if table_name == 'hired_employees':
            model = _models.Employees()
        elif table_name == 'jobs':
            model = _models.Jobs()
        elif table_name == 'departments':
            model = _models.Departments()

        column_names = [column.name for column in model.__table__.columns]
        
        # Read CSV data into a DataFrame
        df = pd.read_csv(file.file, header=None)
        df.columns = column_names
        
        db.begin()
        # Upload data into the database
        df.to_sql(table_name, db.get_bind(), if_exists="append", index=False)
        # Commit the transaction
        db.execute(text(f"SELECT setval('{table_name}_id_seq', max(id)) FROM {table_name};"))
        db.commit()
        return {"message": f"Table {table_name} uploaded successfully"}
        
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="IntegrityError: Duplicate entry")

# Backup selected table  
# Load Avro schema from the selected model
def load_avro_schema(table_name):
    if table_name == 'hired_employees':
        schema_dict: dict = _schemas.Employees.avro_schema()
    elif table_name == 'jobs':
        schema_dict: dict = _schemas.Job.avro_schema()
    elif table_name == 'departments':
        schema_dict: dict = _schemas.Department.avro_schema()
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

def restore_table(db: Session, table_name: str): 
    avro_file_path= f"{table_name}_backup.avro"
    avro_reader  = DataFileReader(open(avro_file_path, "rb"), DatumReader())
    # Iterate through the Avro records and add them to the database
    for avro_record in avro_reader:
        # Create an instance of the AvroData class for each record
        if table_name == 'hired_employees':
            record = _models.Employees(**avro_record)
        elif table_name == 'jobs':
            record = _models.Jobs(**avro_record)
        elif table_name == 'departments':
            record = _models.Departments(**avro_record)

        # Add the record to the session
        db.add(record)
        # Commit the session to save the changes
        db.commit()