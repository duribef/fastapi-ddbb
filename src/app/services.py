import app.database as _database
from typing import List
import app.schemas as _schemas
import app.models as _models
from sqlalchemy.orm import Session

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