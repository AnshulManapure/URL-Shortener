from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import datetime

import models
import database
import utils

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

#Create endpoint to send long url and get short url
@app.post('/shorten', response_model=models.URLResponse)
def create_short_url(payload: models.URLCreate, db: Session = Depends(get_db)):
    new_url = models.URL(original_url = str(payload.original_url))
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    short_code = utils.encode_base62(new_url.id)
    new_url.short_code = short_code

    if payload.expires_in_days:
        new_url.expires_at = datetime.datetime.now() + datetime.timedelta(days=payload.expires_in_days)
    
    db.commit()
    
    return {
        "short_code": short_code,
        "short_url": f"http://localhost:8000/{short_code}",
        "expires_at": new_url.expires_at
    }


@app.get('/{short_code}')
def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):
    url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if url.expires_at < datetime.datetime.now():
        raise HTTPException(status_code=410, detail="Expired URL")
    
    url.click_count += 1    

    click = models.Click(url_id = url.id, 
                         user_agent = request.headers.get('user-agent'),
                         ip_address = request.client.host)
    db.add(click)
    db.commit()

    return RedirectResponse(url=url.original_url, status_code=307)