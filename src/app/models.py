import sqlalchemy as _sql
import app.database as _database
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Employees(_database.Base):
    __tablename__ = "hired_employees"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True, nullable=False, doc='Id of the employee')
    name = _sql.Column(_sql.String, index=False, doc='Name and surename of the employee')
    datetime = _sql.Column(_sql.String, index=False, doc='Hire datetime in ISO format')
    department_id = _sql.Column(_sql.Integer, _sql.ForeignKey('departments.id'), index=True, nullable=True, doc='Id of the department which the employee was hired for')
    job_id = _sql.Column(_sql.Integer,_sql.ForeignKey('jobs.id'), index=True, nullable=True, doc='Id of the job which the employee was hired for')

class Departments(_database.Base):
    __tablename__ = "departments"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True, nullable=False, doc='Id of the department')
    department = _sql.Column(_sql.String, index=False, doc='Name of the department')

class Jobs(_database.Base):
    __tablename__ = "jobs"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True, autoincrement=True, nullable=False, doc='Id of the job')
    job = _sql.Column(_sql.String, index=False, doc='Name of the job')

class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, nullable=False)
    email = _sql.Column(_sql.String, nullable=False, unique=True)
    password = _sql.Column(_sql.String, nullable=False)