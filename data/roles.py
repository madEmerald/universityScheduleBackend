from sqlalchemy import Column, Integer, String
from data.db_session import SqlAlchemyBase


class Role(SqlAlchemyBase):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
