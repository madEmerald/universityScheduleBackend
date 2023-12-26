from sqlalchemy import Column, Integer, String
from data.db_session import SqlAlchemyBase


class Professor(SqlAlchemyBase):
    __tablename__ = 'professors'
    professor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
