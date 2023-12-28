from sqlalchemy import Column, Integer, String
from data.db_session import SqlAlchemyBase


class Classroom(SqlAlchemyBase):
    __tablename__ = 'classrooms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
