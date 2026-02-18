from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel

Base = declarative_base()


"""
Naming Conventions

Class names:
    - PascalCase (First letter of every word capitalized)
    - Singular (User, URL, Click)
    
Table names:
    - lowercase
    - snake_case
    - usually plural (users, urls, clicks)

Column / variable names:
    - lowercase
    - snake_case
    - descriptive

"""

#Defining a table called "users" to store user information
class User(Base): 
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    #Define a python relationship b/w 2 columns of 2 tables.
    #Here the column "owner" of the class "URL" mathces with the column "urls" of class "Users."
    #Similarly, we need a column "owner" in class "URL" that matches with this column
    urls = relationship("URL", back_populates="owner") 


#Defining a table called "urls" to store shortened urls. 
#Foreign key is defined using ForeignKey("table_name.column_name"). ondelete cascade means that if the user is deleted all rown referencing the user are also deleted.
class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    click_count = Column(Integer, default=0)
    owner = relationship("User", back_populates="urls")


class Click(Base):
    __tablename__ = "clicks"
    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), index=True)
    timestamp = Column(DateTime, server_default=func.now())
    user_agent = Column(String)
    ip_address = Column(String)

