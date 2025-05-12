from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Swince(Base) :
    __tablename__ = 'swince'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    origin = Column(String(50))

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class Originator(Base):
    __tablename__ = 'originator'
    id = Column(Integer, primary_key=True, autoincrement=True)
    swince_id = Column(Integer, ForeignKey('swince.id'), nullable=False)
    originator_id = Column(Integer, ForeignKey('user.id'), nullable=False)

class Target(Base):
    __tablename__ = 'target'
    id = Column(Integer, primary_key=True, autoincrement=True)
    swince_id = Column(Integer, ForeignKey('swince.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('user.id'), nullable=False)

class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    content = Column(String(200), nullable=False)
    author = Column(String(50), ForeignKey('user.id'), nullable=False)