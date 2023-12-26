from sqlalchemy import Column, Integer, CheckConstraint, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from data.db_session import SqlAlchemyBase


class Class(SqlAlchemyBase):
    __tablename__ = 'classes'
    class_time_id = Column(Integer, primary_key=True, autoincrement=True)
    start = Column(Time)
    end = Column(Time)
    class_number = Column(Integer)
    weekday = Column(Integer)
    week_parity = Column(Integer)
    subject_id = Column(Integer, ForeignKey('subjects.subject_id', ondelete='SET NULL'))
    semester_id = Column(Integer, ForeignKey('semesters.semester_id', ondelete='SET NULL'))
    professor_id = Column(Integer, ForeignKey('professors.professor_id', ondelete='SET NULL'))
    classroom_id = Column(Integer, ForeignKey('classrooms.classroom_id', ondelete='SET NULL'))
    group_id = Column(Integer, ForeignKey('groups.group_id', ondelete='SET NULL'))

    check_week_parity = CheckConstraint("week_parity >= 1 AND week_parity <= 2")
    check_weekday = CheckConstraint("weekday >= 1 AND weekday <= 7")

    UniqueConstraint('class_number', 'weekday', 'week_parity', 'semester_id', 'professor_id')
    UniqueConstraint('class_number', 'weekday', 'week_parity', 'semester_id', 'classroom_id')
    UniqueConstraint('class_number', 'weekday', 'week_parity', 'semester_id', 'group_id')

    subject = relationship("Subjects")
    semester = relationship("Semesters")
    professor = relationship("Professors")
    classroom = relationship("Classrooms")
    group = relationship("Groups")
