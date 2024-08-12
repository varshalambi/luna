from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse,FileResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import shutil
import os
from typing import List
from confluent_kafka import Producer
from tempfile import NamedTemporaryFile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from foodlabel import get_all

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



DATABASE_URL = "mysql+mysqlconnector://zmuser:zmpass@localhost:3306/zm"
engine = create_engine(DATABASE_URL)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# SQLAlchemy ORM setup
Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    homeview = Column(String)  # Assuming home_view is a string representation

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


Base.metadata.create_all(bind=engine)

# Session management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    email: str
    phone: str
    homeview: str
    
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    homeview: str


# class UserInDB(User):
#     password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app = APIRouter()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user != None:
        return user


async def authenticate_user(input_username: str, input_password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == input_username).first()
    print(user)
    if not user:
        return False
    if not verify_password(input_password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    print("hellp", token)
    db = SessionLocal()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
             return None, False
        token_data = TokenData(username=username)
    except JWTError:
        # raise credentials_exception
        return None, False
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
         return None, False
    return user , True


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/create_user", response_model=UserResponse)
def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        username=user.username,
        password=get_password_hash(user.password),  # Hash the password
        name=user.name,
        email=user.email,
        phone=user.phone,
        homeview=user.homeview
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login",tags=['users'])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],) -> Token:
    print("form data",form_data.password)
    db = SessionLocal()
    # user = db.query(User).filter(User.username == form_data.username).first()
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/isLoggedIn",tags=['users'])
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
):
    print(current_user[0].username)
    output = {
        "isLoggedIn" : current_user[1]
    }
    return output

# @app.post("/upload")
# async def upload_image(current_user: Annotated[User, Depends(get_current_user)],file: UploadFile = File(...)):
#     try:
#         # Save the uploaded file to the specified directory
#         username = current_user[0].username
#         UPLOAD_DIRECTORY = "/home/ubuntu/users/monitors/{}/input".format(username)
#         print(file.filename)
#         with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
        
#         return JSONResponse(status_code=200, content={"message": "File uploaded successfully"})
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": str(e)})
def delivery_callback(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to topic {msg.topic()} [partition {msg.partition()}]")

def produce_image(producer, topic, image_data):
    producer.produce(topic, value=image_data, callback=delivery_callback)
    producer.poll(0)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Save uploaded image to a temporary file
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name
        
        # Kafka configuration
        kafka_conf = {
            'bootstrap.servers': 'localhost:29092',  # Kafka broker
        }

        # Create Kafka producer
        producer = Producer(kafka_conf)

        # Produce image
        topic = 'image_topic'
        with open(temp_file_path, "rb") as image_file:
            image_data = image_file.read()
            produce_image(producer, topic, image_data)

        # Flush messages and close producer
        producer.flush()

        # Return response
        return {"message": "Image uploaded successfully and sent to Kafka."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        # Delete temporary file
        os.unlink(temp_file_path)

@app.get("/get_results")
async def get_results(id: str = None):
    id = 'last'
    if id:
       data = get_all.get_from_db(id)
    else:
       data = get_all.get_from_db()
    dummy_data = {
        "status": "success",
        "data": {
            "message": "Database Results",
            "items": data
        }
    }
    return JSONResponse(content=dummy_data)

@app.get("/images/")
async def get_files(current_user : Annotated[User, Depends(get_current_active_user)]):
    try:
        username = current_user[0].username
        FILES_DIRECTORY = "/home/ubuntu/users/monitors/{}/input".format(username)
        file_names = os.listdir(FILES_DIRECTORY)
        print(FILES_DIRECTORY)
        for file_name in file_names:
            file_path = os.path.join(FILES_DIRECTORY, file_name)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File '{file_name}' not found")
        return {
            "files": [
                FileResponse(os.path.join(FILES_DIRECTORY, file_name), filename=file_name)
                for file_name in file_names
            ]
        }
    except Exception as e:
        return {"Error" : str(e)}

SHARE_DIRECTORY = '/home/ubuntu/users/monitors/{}/input'.format('gagan')
@app.get("/files/")
async def list_files():
    files = os.listdir(SHARE_DIRECTORY)
    return {"files": files}

@app.get("/files/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(SHARE_DIRECTORY, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Define the Item model
class Item(BaseModel):
    text: str
    imageUrl: str

# In-memory "database" of items
items_db = [
        Item(text="First item", imageUrl="http://13.200.194.74/images/first.jpg"),
        Item(text="Second item", imageUrl="http://13.200.194.74/images/second.jpg"),
]

# API endpoint to get all items
@app.get("/get_all", response_model=List[Item])
async def get_all_items():
    try:
        if items_db:
            return items_db
        else:
            raise HTTPException(status_code=404, detail="No items found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/images")
async def get_images():
      raise HTTPException(status_code=404, detail="No items found")
