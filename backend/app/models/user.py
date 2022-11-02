from sqlalchemy import Integer, Text, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(Text, nullable=False)
    age = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
