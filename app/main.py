from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from jose import jwt 
import datetime
from dotenv import load_dotenv
import os
from redis.exceptions import RedisError

import models
import database
import utils
import auth
import cache

#Loading environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
RATE_LIMIT = os.getenv("RATE_LIMIT")
RATE_LIMIT_WINDOW = os.getenv("RATE_LIMIT_WINDOW")

#Initialise FastAPI app
app = FastAPI()

#Initialise the database if empty
models.Base.metadata.create_all(bind=database.engine)

#Define a function that provides db object to any function that needs it and then closes the db object
def get_db():
    db = database.session()
    try:
        yield db
    finally:
        db.close_all()

#Define a function to get user on every API call
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") #Get bearer token from user request everytime login endpoint is hit succesfully
def get_current_user(token: str=Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
    user = db.query(models.User).filter(models.User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(401)    
    return user

#Function to check if redis is up and available
def check_redis():    
    redis_available = True
    try:
        cache.redis_client.ping()
    except RedisError:
        redis_available = False
    return redis_available

#Create endpoint to send long url and get short url
@app.post('/shorten', response_model=models.URLResponse)
def create_short_url(payload: models.URLCreate, request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):    
    #Adding rate limiting through redis
    cache_key = f"rate_limit:{current_user.id}"
    count = cache.redis_client.get(cache_key)
    if count == None:
        cache.redis_client.set(name=cache_key, value=1, ex=RATE_LIMIT_WINDOW) #Initialises the key to 1 and sets expiry for 60s, so the counter is reset every 60s
    elif int(count) >= int(RATE_LIMIT):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    else:
        cache.redis_client.incr(name=cache_key, amount=1)

    #Adding new url to db
    new_url = models.URL(original_url = str(payload.original_url),
                         user_id = current_user.id)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    short_code = utils.encode_base62(new_url.id)
    new_url.short_code = short_code

    short_url = f"{request.base_url}{short_code}"

    if payload.expires_in_days:
        new_url.expires_at = datetime.datetime.now() + datetime.timedelta(days=payload.expires_in_days)
    
    db.commit()
    
    return {
        "short_code": short_code,
        "short_url": short_url,
        "expires_at": new_url.expires_at
    }


#Endpoint to redirect
@app.get('/{short_code}')
def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):
    cache_key = f"url:{short_code}"
    redis_available = check_redis()
    
    if redis_available:
        cache_url = cache.redis_client.get(cache_key)
    else:
        cache_url = None

    if cache_url:
        return RedirectResponse(url=cache_url, status_code=307)
    
    url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if url.expires_at and url.expires_at < datetime.datetime.now():
        raise HTTPException(status_code=410, detail="Expired URL")
    
    #Store in redis cache
    if redis_available:
        cache.redis_client.set(name=cache_key, value=url.original_url, ex=3600) #Cache entry expires in 3600s, i.e, 1 hour
    
    #Update click metrics
    url.click_count += 1    

    click = models.Click(url_id = url.id, 
                        user_agent = request.headers.get('user-agent'),
                        ip_address = request.client.host)
    db.add(click)
    db.commit()

    return RedirectResponse(url=url.original_url, status_code=307)


#Endpoint to register a new user
@app.post('/register')
def user_register(payload: models.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(400, "User already exists.")
    
    hashed_password = auth.hash_password(payload.password)

    new_user = models.User(
        email=payload.email,
        hashed_password = hashed_password)
    
    db.add(new_user)
    db.commit()

    return {"message": "User created succesfully."}


#Endpoint to login
#Swagger sends oauth2 form in the form of username and password to the login endpoint in order to generate jwt and store it.
#So we need to use the OAuth2PasswordRequestForm and the keywords "username" and "password"
@app.post('/login')
def user_login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.username).first()

    if not user:
        raise HTTPException(400, "Invalid email or password")

    valid_user = auth.verify_password(payload.password, user.hashed_password)

    if not valid_user:
        raise HTTPException(401, "Unauthorised")
    
    jwt = auth.create_jwt({"sub": str(user.id)})
    
    return {
        "access_token": jwt,
        "token_type": "bearer"
    }

@app.get('/analytics/{short_code}')
def get_analytics(short_code: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not url:
        raise HTTPException(404, 'Invalid URL.')
    
    if current_user.id != url.user_id:
        raise HTTPException(403)

    clicks_per_day = (        
        db.query(
            func.date(models.Click.timestamp),
            func.count(models.Click.id)
        )
        .filter(models.Click.url_id == url.id)
        .group_by(func.date(models.Click.timestamp))
        .order_by(func.date(models.Click.timestamp))
        .all()
    )

    #clicks_per_day is a list of rows. Each row contains a date and the amount of clicks on that day.
    #We need to return each row in the format of the pydantic model defined in Models.py
    metrics_list = []
    for row in clicks_per_day:
        metrics_list.append(
            models.Metrics(
                short_code=short_code,
                original_url=url.original_url,
                created_at=url.created_at,
                expires_at=url.expires_at,
                date=row[0],
                total_clicks=row[1]                
            )
        )
        
    return metrics_list
    

