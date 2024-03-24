from fastapi import FastAPI, Depends, UploadFile, File, Query
import app.services as _services
import app.schemas as _schemas
from typing import List
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
import asyncio

app = FastAPI()

# Create tables
_services._add_tables()

# Move historical data to hired_employees table
@app.post("/api/batch")
async def upload_file(
    file: UploadFile = File(...), 
    db: Session = Depends(_services.get_db)):
    return await _services.upload_csv_to_database(file=file, db=db)

# Back up table to AVRO
@app.post("/api/create_backup", status_code=200)
async def backup_table(
    table_name: _schemas.DropdownOptions = Query(..., description="Select a table to backup"),
    db: Session = Depends(_services.get_db),
):
    try:
        backup_file_path = await asyncio.to_thread(_services.backup_table_to_avro, db=db, table_name=table_name.value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"message": f"Backup of table {table_name.value} stored in {backup_file_path}"}

@app.post("/api/restore_backup")
async def restore_table(
    table_name: _schemas.DropdownOptions = Query(..., description="Select a table to restore"),
    db: Session = Depends(_services.get_db)):
    _services.restore_table(db, table_name.value)
    return {"message": "Avro data imported successfully"}

# Add new data to hired_employees table
@app.post("/api/employees/", response_model=List[_schemas.Employees])
async def create_employees(
    employees: List[_schemas.EmployeesCreate],
    db: Session = Depends(_services.get_db),
):
    if len(employees) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_employees(employees=employees, db=db)

# Add new data to department table
@app.post("/api/department/", response_model=List[_schemas.Department])
async def create_department(
    departments: List[_schemas.DepartmentCreate],
    db: Session = Depends(_services.get_db),
):
    if len(departments) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_departments(departments=departments, db=db)

# Add new data to jobs table
@app.post("/api/jobs/", response_model=List[_schemas.Job])
async def create_jobs(
    jobs: List[_schemas.JobCreate],
    db: Session = Depends(_services.get_db),
):
    if len(jobs) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_jobs(jobs=jobs, db=db)