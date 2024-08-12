from fastapi import FastAPI, File, UploadFile,Request
from fastapi.responses import JSONResponse
import shutil
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



DATABASE_URL = "mysql+mysqlconnector://zmuser:zmpass@localhost:3306/zm"
engine = create_engine(DATABASE_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# SQLAlchemy ORM setup
Base = declarative_base()

app = APIRouter()

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    homeview = Column(String)  # Assuming home_view is a string representation


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    db = SessionLocal()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
             return None
        token_data = TokenData(username=username)
    except JWTError:
        # raise credentials_exception
        return None
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
         return None, False
    return user 


@app.post("/upload")
async def upload_image(request : Request,current_user: Annotated[User, Depends(get_current_user)],file: UploadFile = File(...)):
    print(request.method)
    print(request)
    try:
        # Save the uploaded file to the specified directory

        username = current_user[0].username
        UPLOAD_DIRECTORY = "/home/ubuntu/users/monitors/{}/input".format(username)
        with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return JSONResponse(status_code=200, content={"message": "File uploaded successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

