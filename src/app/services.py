import app.database as _database
from typing import List
import app.schemas as _schemas
import app.models as _models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import pandas as pd
from fastapi.exceptions import HTTPException
from sqlalchemy import text

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

# Add Data Logic
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

def upload_csv_to_database(file, db: Session):
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