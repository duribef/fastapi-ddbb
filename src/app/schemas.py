from pydantic import BaseModel


class EmployeesBase(BaseModel):
    name: str  
    datetime: str 
    department_id: int
    job_id: int

class EmployeesCreate(EmployeesBase):
    pass

class Employees(EmployeesBase):
    __tablename__ = 'hired_employees'
    id: int
    class Config:
        orm_mode = True