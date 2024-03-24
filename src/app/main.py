from fastapi import FastAPI, Depends
import app.services as _services
import app.schemas as _schemas
from typing import List
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

app = FastAPI()

# Create tables
_services._add_tables()

# Add new data to hired_employees table
@app.post("/api/employees/", response_model=List[_schemas.Employees])
async def create_employees(
    employees: List[_schemas.EmployeesCreate],
    db: Session = Depends(_services.get_db),
):
    if len(employees) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_employees(employees=employees, db=db)