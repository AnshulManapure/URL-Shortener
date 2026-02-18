from fastapi import FastAPI
from sqlalchemy.orm import Session

import models
import database

app = FastAPI()

#Initialise the database if empty
models.Base.metadata.create_all(bind=database.engine)