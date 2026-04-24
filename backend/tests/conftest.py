"""Pytest 配置和通用 fixtures"""
import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from extensions import db
from models import Room, Teacher, Class, Course, Holiday, TeachingClass, ScheduleEntry


@pytest.fixture(scope='session')
def app():
    """创建测试应用实例"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建 CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def session(app):
    """创建数据库会话"""
    with app.app_context():
        yield db.session


@pytest.fixture
def sample_rooms(session):
    """创建测试教室"""
    rooms = [
        Room(room_number='R001', name='101教室', capacity=50, room_type='普通教室'),
        Room(room_number='R002', name='201教室', capacity=60, room_type='多媒体教室'),
        Room(room_number='R003', name='301机房', capacity=40, room_type='机房'),
        Room(room_number='R004', name='401实验室', capacity=30, room_type='实验室'),
    ]
    for room in rooms:
        session.add(room)
    session.commit()
    return rooms


@pytest.fixture
def sample_teachers(session):
    """创建测试教师"""
    teachers = [
        Teacher(
            teacher_number='T001', name='张老师',
            teachable_courses=['数学', '物理'],
            max_classes=3, max_weekly_sessions=5
        ),
        Teacher(
            teacher_number='T002', name='李老师',
            teachable_courses=['英语', '语文'],
            max_classes=4, max_weekly_sessions=4
        ),
    ]
    for teacher in teachers:
        session.add(teacher)
    session.commit()
    return teachers


@pytest.fixture
def sample_classes(session):
    """创建测试班级"""
    classes = [
        Class(class_number='C001', name='计算机1班', student_count=40, department='计算机系'),
        Class(class_number='C002', name='数学1班', student_count=35, department='数学系'),
    ]
    for cls in classes:
        session.add(cls)
    session.commit()
    return classes


@pytest.fixture
def sample_holidays(session):
    """创建测试节假日"""
    holidays = []
    for i in range(5):
        h = Holiday(
            date=datetime.now() + timedelta(days=10 + i),
            name='测试节假日'
        )
        session.add(h)
        holidays.append(h)
    session.commit()
    return holidays
