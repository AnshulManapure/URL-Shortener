from passlib.context import CryptContext
from jose import jwt

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

#Loading environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#Create a configurator that can be used to hash passwords and to verify them later
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

#Define functions to hash and verify passwords
def hash_password(plain_password: str):
    return pwd_context.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


#JWT Setup
def create_jwt(data: dict):
    to_encode = data.copy() #Dont want to modify original data
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
