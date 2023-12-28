from sqlalchemy import Column, Integer, CheckConstraint, Time, ForeignKey, UniqueConstraint

from data.db_session import SqlAlchemyBase


class Class(SqlAlchemyBase):
    __tablename__ = 'classes'
    __table_args__ = (UniqueConstraint('class_number', 'weekday', 'week_parity', 'professor_id'),
                      UniqueConstraint('class_number', 'weekday', 'week_parity', 'classroom_id'),
                      UniqueConstraint('class_number', 'weekday', 'week_parity', 'group_id'))
    id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(Time)
    end = Column(Time)
    class_number = Column(Integer)
    weekday = Column(Integer)
    week_parity = Column(Integer)
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'))
    professor_id = Column(Integer, ForeignKey('professors.id', ondelete='SET NULL'))
    classroom_id = Column(Integer, ForeignKey('classrooms.id', ondelete='SET NULL'))
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='SET NULL'))

    check_week_parity = CheckConstraint("week_parity >= 1 AND week_parity <= 2")
    check_weekday = CheckConstraint("weekday >= 1 AND weekday <= 7")
