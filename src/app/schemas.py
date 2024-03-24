from pydantic import BaseModel
from enum import Enum
from pydantic import Field
from typing_extensions import Annotated
from typing import Optional
from pydantic_avro.base import AvroBase

class EmployeesBase(AvroBase):
    name: Optional[Annotated[str, Field(strict=False)]]  
    datetime: Optional[Annotated[str, Field(strict=False)]] 
    department_id: Optional[Annotated[int, Field(strict=False, gt=0)]]
    job_id: Optional[Annotated[int, Field(strict=False, gt=0)]]

class EmployeesCreate(EmployeesBase):
    pass

class Employees(EmployeesBase):
    __tablename__ = 'hired_employees'
    id: int
    class Config:
        orm_mode = True

class JobBase(AvroBase):
    __tablename__ = 'jobs'
    job: Optional[Annotated[str, Field(strict=False)]]

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    class Config:
        orm_mode = True

class DepartmentBase(AvroBase):
    __tablename__ = 'department'
    department: Optional[Annotated[str, Field(strict=False)]]

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    class Config:
        orm_mode = True

class DropdownOptions(str, Enum):
    hired_employees = "hired_employees"
    jobs = "jobs"
    department = "departments"

class DropdownOptions(str, Enum):
    hired_employees = "hired_employees"
    jobs = "jobs"
    department = "departments"