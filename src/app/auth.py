import os
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import app.schemas as _schemas
from fastapi import Depends, status, HTTPException

# Create instance of bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to verify the pasword vs hashed password in the db
def verify(password, hashed_password):
    try:
        return pwd_context.verify(password, hashed_password)
    except UnknownHashError:
        return False
# Create an access token with the given data plus an exp time
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')))

    to_encode.update(dict(exp=expire))

    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try:
        # Read the payload in the bearer token
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = _schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    return verify_access_token(token, credentials_exception)