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

class DropdownOptions(str, Enum):
    hired_employees = "hired_employees"
    jobs = "jobs"
    department = "departments"