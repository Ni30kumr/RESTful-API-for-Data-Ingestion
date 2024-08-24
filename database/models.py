from database.data import Base
from sqlalchemy import create_engine, Column, Integer, String, Date,ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    first_name = Column(String(50))
    last_name = Column(String(50))

    your_data = relationship("YourData", back_populates="user")

class YourData(Base):
    __tablename__ = "your_data"

    pri_key = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(Integer, ForeignKey('users.id'))
    document_id = Column(Integer,  default=None)
    username = Column(String(50), default=None)
    email = Column(String(100),  default=None)
    path = Column(String(255), nullable=True, default=None)

    user = relationship("User", back_populates="your_data")