from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(String(120), nullable=False)
    email = Column(String(120), unique=True)
    password = Column(String(255), nullable=False)
    created = Column(DateTime, default=datetime.now())
