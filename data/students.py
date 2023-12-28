from sqlalchemy import Column, Integer, String, ForeignKey
from data.db_session import SqlAlchemyBase


class Student(SqlAlchemyBase):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), unique=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'))
    name = Column(String)
