from extensions import db


class BaseModel(db.Model):
    """基础模型类，提供公共字段"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = db.Column(db.DateTime, server_default=db.func.now(), comment="创建时间")
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        comment="更新时间",
    )


class Room(BaseModel):
    """教室模型"""
    __tablename__ = 'rooms'

    ROOM_TYPES = ['普通教室', '多媒体教室', '机房', '实验室']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    room_number = db.Column(db.String(50), unique=True, nullable=False, comment="教室编号")
    name = db.Column(db.String(100), nullable=False, comment="教室名称")
    capacity = db.Column(db.Integer, nullable=False, comment="容量")
    room_type = db.Column(db.String(50), nullable=False, comment="教室类型")
    is_available = db.Column(db.Boolean, default=True, nullable=False, comment="可用状态")

    schedule_entries = db.relationship('ScheduleEntry', backref='room', lazy=True)
    teaching_classes = db.relationship('TeachingClass', backref='assigned_room', lazy=True)

    def __repr__(self):
        return f'<Room {self.room_number} - {self.name}>'


class Teacher(BaseModel):
    """教师模型"""
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    teacher_number = db.Column(db.String(50), unique=True, nullable=False, comment="教师编号")
    name = db.Column(db.String(100), nullable=False, comment="姓名")
    teachable_courses = db.Column(db.JSON, nullable=True, comment="可授课程列表")
    max_classes = db.Column(db.Integer, default=5, nullable=False, comment="授课班级上限")
    max_weekly_sessions = db.Column(db.Integer, default=5, nullable=False, comment="每周课次上限")

    courses = db.relationship('Course', backref='teacher', lazy=True)
    teaching_classes = db.relationship('TeachingClass', backref='teacher', lazy=True)

    def __repr__(self):
        return f'<Teacher {self.teacher_number} - {self.name}>'


class Class(BaseModel):
    """班级模型"""
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    class_number = db.Column(db.String(50), unique=True, nullable=False, comment="班级编号")
    name = db.Column(db.String(100), nullable=False, comment="班级名称")
    student_count = db.Column(db.Integer, nullable=False, comment="学生人数")
    department = db.Column(db.String(100), nullable=True, comment="所属专业/年级")

    courses = db.relationship('Course', backref='class_', lazy=True)
    teaching_classes = db.relationship('TeachingClass', backref='class_', lazy=True)

    def __repr__(self):
        return f'<Class {self.class_number} - {self.name}>'


class Course(BaseModel):
    """课程模型"""
    __tablename__ = 'courses'

    COURSE_TYPES = ['普通授课', '实验', '上机']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    course_number = db.Column(db.String(50), unique=True, nullable=False, comment="课程编号")
    name = db.Column(db.String(100), nullable=False, comment="课程名称")
    course_type = db.Column(db.String(50), nullable=False, comment="课程类型")
    total_hours = db.Column(db.Integer, default=64, nullable=False, comment="总课时")
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True, comment="授课教师ID")
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True, comment="授课班级ID")

    teaching_classes = db.relationship('TeachingClass', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.course_number} - {self.name}>'


class Holiday(BaseModel):
    """节假日模型"""
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    date = db.Column(db.Date, nullable=False, comment="日期")
    name = db.Column(db.String(100), nullable=False, comment="节假日名称")

    def __repr__(self):
        return f'<Holiday {self.date} - {self.name}>'


class TeachingClass(BaseModel):
    """教学班模型"""
    __tablename__ = 'teaching_classes'

    TIME_PERIODS = ['morning', 'afternoon', 'evening']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, comment="课程ID")
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False, comment="班级ID")
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False, comment="教师ID")
    assigned_room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True, comment="分配的教室ID")
    assigned_day = db.Column(db.Integer, nullable=False, comment="分配的星期（1-5）")
    assigned_period = db.Column(db.String(20), nullable=False, comment="分配的大时段")

    schedule_entries = db.relationship('ScheduleEntry', backref='teaching_class', lazy=True)

    def __repr__(self):
        return f'<TeachingClass {self.id}>'


class ScheduleEntry(BaseModel):
    """课表记录模型"""
    __tablename__ = 'schedule_entries'

    TIME_PERIODS = ['morning', 'afternoon', 'evening']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    teaching_class_id = db.Column(db.Integer, db.ForeignKey('teaching_classes.id'), nullable=False, comment="教学班ID")
    week = db.Column(db.Integer, nullable=False, comment="周次（1-16）")
    day = db.Column(db.Integer, nullable=False, comment="星期（1-5）")
    period = db.Column(db.String(20), nullable=False, comment="大时段")
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False, comment="教室ID")
    is_holiday = db.Column(db.Boolean, default=False, nullable=False, comment="是否节假日")

    def __repr__(self):
        return f'<ScheduleEntry Week{self.week}-Day{self.day}-{self.period}>'
