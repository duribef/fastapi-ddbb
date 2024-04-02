from fastapi import FastAPI, Depends, UploadFile, File, Query, status
import app.services as _services
import app.schemas as _schemas
import app.models as _models
from typing import List
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from app.logging.exception_handlers import request_validation_exception_handler, http_exception_handler, unhandled_exception_handler
from app.logging.middleware import log_request_middleware

from fastapi.security.oauth2 import OAuth2PasswordRequestForm
import app.auth as _auth

app = FastAPI()

app.middleware("http")(log_request_middleware)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Create tables
_services._add_tables()

@app.post('/api/auth/token', response_model=_schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(_services.get_db)):
    user = db.query(_models.User).filter(
        _models.User.email == user_credentials.username).first()
   
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not _auth.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    access_token = _auth.create_access_token(data={"user_id": user.email})

    return {"access_token": access_token}

# Move historical data to hired_employees table
@app.post("/api/batch")
async def upload_file(
    file: UploadFile = File(...), 
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    return await _services.upload_csv_to_database(file=file, db=db)

# Back up table to AVRO
@app.post("/api/create_backup", status_code=200)
async def backup_table(
    table_name: _schemas.DropdownOptions = Query(..., description="Select a table to backup"),
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    try:
        backup_file_path = _services.backup_table_to_avro(db=db, table_name=table_name.value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {f"File {table_name.value} uploaded to Google Cloud Storage."}

@app.post("/api/restore_backup")
async def restore_table(
    table_name: _schemas.DropdownOptions = Query(..., description="Select a table to restore"),
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    _services.restore_table(db, table_name.value)
    return {"message": "Avro data imported successfully"}

# Add new data to hired_employees table
@app.post("/api/employees/", response_model=List[_schemas.Employees])
async def create_employees(
    employees: List[_schemas.EmployeesCreate],
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    if len(employees) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_employees(employees=employees, db=db)

# Add new data to department table
@app.post("/api/department/", response_model=List[_schemas.Department])
async def create_department(
    departments: List[_schemas.DepartmentCreate],
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    if len(departments) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_departments(departments=departments, db=db)

# Add new data to jobs table
@app.post("/api/jobs/", response_model=List[_schemas.Job])
async def create_jobs(
    jobs: List[_schemas.JobCreate],
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    if len(jobs) > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")
    return await _services.create_jobs(jobs=jobs, db=db)

# Challenge 2
@app.get("/api/metric1/")
async def metric1(
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    try:
        return await _services.metric1(db)
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/api/metric2/")
async def metric1(
    db: Session = Depends(_services.get_db),
    current_user: int = Depends(_auth.get_current_user)):
    try:
        return await _services.metric2(db)
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

