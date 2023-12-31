from sqlalchemy import Column, Integer, String, ForeignKey
from data.db_session import SqlAlchemyBase


class Professor(SqlAlchemyBase):
    __tablename__ = 'professors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), unique=True)
    name = Column(String)
