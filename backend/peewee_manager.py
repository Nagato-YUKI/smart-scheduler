from peewee import *
from config import Config

# 根据配置选择数据库类型
if Config.DB_TYPE == "postgresql":
    from playhouse.db_url import connect
    _database = connect(Config.DATABASE)
else:
    _database = SqliteDatabase(Config.DATABASE)

def get_db():
    return _database


class BaseModel(Model):
    class Meta:
        database = _database

    id = AutoField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    updated_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Room(BaseModel):
    room_number = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    capacity = IntegerField()
    room_type = CharField(max_length=50)
    is_available = BooleanField(default=True)


class Teacher(BaseModel):
    teacher_number = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    teachable_courses = TextField(null=True)
    max_classes = IntegerField(default=5)
    max_weekly_sessions = IntegerField(default=5)


class SchoolClass(BaseModel):
    class_number = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    student_count = IntegerField()
    department = CharField(max_length=100, null=True)


class Course(BaseModel):
    course_number = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    course_type = CharField(max_length=50)
    total_hours = IntegerField(default=64)
    teacher = ForeignKeyField(Teacher, backref='courses', null=True)
    school_class = ForeignKeyField(SchoolClass, backref='courses', null=True)


class Holiday(BaseModel):
    date = DateField()
    name = CharField(max_length=100)


class TeachingClass(BaseModel):
    course = ForeignKeyField(Course, backref='teaching_classes')
    school_class = ForeignKeyField(SchoolClass, backref='teaching_classes')
    teacher = ForeignKeyField(Teacher, backref='teaching_classes')
    assigned_room = ForeignKeyField(Room, backref='teaching_classes', null=True)
    assigned_day = IntegerField()
    assigned_period = CharField(max_length=20)


class ScheduleEntry(BaseModel):
    teaching_class = ForeignKeyField(TeachingClass, backref='schedule_entries')
    week = IntegerField()
    day = IntegerField()
    period = CharField(max_length=20)
    room = ForeignKeyField(Room, backref='schedule_entries')
    is_holiday = BooleanField(default=False)
