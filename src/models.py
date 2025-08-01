from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    macros = relationship("Macro", uselist=False, back_populates="user", cascade="all, delete-orphan")
    history = relationship("MacroHistory", back_populates="user", cascade="all, delete-orphan")


class Macro(Base):
    __tablename__ = 'macros'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    date = Column(Date, nullable=False)
    calorie = Column(Float, default=0)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)

    user = relationship("User", back_populates="macros")


class MacroHistory(Base):
    __tablename__ = 'macros_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(Date)
    calorie = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)

    user = relationship("User", back_populates="history")
