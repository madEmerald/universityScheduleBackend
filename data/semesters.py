from sqlalchemy import Column, Integer, CheckConstraint
from data.db_session import SqlAlchemyBase


class Semester(SqlAlchemyBase):
    __tablename__ = 'semesters'
    semester_id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer)
    halfyear = Column(Integer)
    check_halfyear = CheckConstraint("halfyear >= 1 AND halfyear <= 2")
