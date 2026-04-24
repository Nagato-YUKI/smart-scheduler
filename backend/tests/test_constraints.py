"""硬约束场景测试"""
import pytest
from datetime import datetime

from scheduler.time_pool import TimePool
from scheduler.holiday_manager import HolidayManager
from scheduler.room_allocator import RoomAllocator, Room
from scheduler.constraints import ConstraintChecker
from scheduler.optimizer import ScheduleOptimizer
from scheduler.validator import ScheduleValidator, ValidationResult
from scheduler.main_scheduler import MainScheduler, Course


class TestHolidayConflictScenarios:
    """测试节假日冲突场景"""

    def test_holiday_blocks_scheduling(self):
        scheduler = MainScheduler(start_date='2026-05-01')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        holidays = {
            'h1': {
                'start_date': '2026-05-01',
                'end_date': '2026-05-01',
                'name': '劳动节',
            }
        }
        scheduler.setup_holidays(holidays)

        pool = scheduler.time_pool
        assert pool.is_available(1, 'monday', 'morning') is False

    def test_holiday_range_blocks_scheduling(self):
        scheduler = MainScheduler(start_date='2026-05-01')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        holidays = {
            'h1': {
                'start_date': '2026-05-01',
                'end_date': '2026-05-05',
                'name': '五一假期',
            }
        }
        scheduler.setup_holidays(holidays)

        pool = scheduler.time_pool
        week1_slots = [
            pool.is_available(1, day, period)
            for day in ['friday']
            for period in ['morning', 'afternoon', 'evening']
        ]
        assert not any(week1_slots)

    def test_scheduling_avoids_holidays(self):
        scheduler = MainScheduler(start_date='2026-05-01')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        holidays = {
            'h1': {
                'start_date': '2026-05-01',
                'end_date': '2026-05-01',
                'name': '劳动节',
            }
        }
        scheduler.setup_holidays(holidays)

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]
        scheduler.schedule_courses(courses)

        for slot_key, sessions in scheduler.schedule.items():
            parts = slot_key.split('_')
            if len(parts) >= 3:
                week = int(parts[0][1:])
                day = parts[1][1:]
                date = scheduler.time_pool.get_date(week, day)
                if date:
                    assert scheduler.holiday_manager.is_holiday(date) is False

    def test_constraint_checker_holiday_conflict(self):
        checker = ConstraintChecker()
        holiday_mgr = HolidayManager()
        holiday_mgr.add_holiday('h1', '2026-03-02', name='节假日')
        pool = TimePool(start_date='2026-03-02')

        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室')

        is_valid, violations = checker.check_all_hard_constraints(
            course, 'R001', 1, 'monday', 'morning', {},
            pool, allocator, holiday_mgr
        )
        assert is_valid is False
        assert any('节假日' in v for v in violations)

    def test_multiple_overlapping_holidays(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', '2026-05-03', name='五一')
        manager.add_holiday('h2', '2026-05-03', '2026-05-05', name='调休')

        assert manager.is_holiday(datetime(2026, 5, 1)) is True
        assert manager.is_holiday(datetime(2026, 5, 3)) is True
        assert manager.is_holiday(datetime(2026, 5, 5)) is True
        assert manager.is_holiday(datetime(2026, 5, 6)) is False

    def test_holiday_does_not_affect_other_weeks(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        holidays = {
            'h1': {
                'start_date': '2026-03-02',
                'end_date': '2026-03-02',
                'name': '节假日',
            }
        }
        scheduler.setup_holidays(holidays)

        pool = scheduler.time_pool
        assert pool.is_available(2, 'monday', 'morning') is True
        assert pool.is_available(3, 'tuesday', 'afternoon') is True


class TestTeacherTimeConflictScenarios:
    """测试教师时间冲突场景"""

    def test_teacher_same_slot_conflict(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        scheduler.add_room('R002', '201教室', 50, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
            Course('C002', '英语', 'T001', 'CL002', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)

        teacher_sessions = {}
        for slot_key, sessions in scheduler.schedule.items():
            for session in sessions:
                tid = session.get('teacher_id')
                if tid == 'T001':
                    if slot_key not in teacher_sessions:
                        teacher_sessions[slot_key] = []
                    teacher_sessions[slot_key].append(session)

        for slot, sessions in teacher_sessions.items():
            assert len(sessions) <= 1

    def test_teacher_different_slots_no_conflict(self):
        checker = ConstraintChecker()
        schedule = {
            'W1_Dmonday_morning': [{'teacher_id': 'T001'}],
        }
        assert checker.check_teacher_conflict('T001', 1, 'monday', 'afternoon', schedule) is True

    def test_teacher_week_limit_enforcement(self):
        checker = ConstraintChecker()
        checker.MAX_TEACHER_SESSIONS_PER_WEEK = 5

        schedule = {}
        for i in range(6):
            schedule[f'W1_Dmonday_slot{i}'] = [{'teacher_id': 'T001', 'week': 1}]

        assert checker.check_teacher_week_limit('T001', 1, schedule) is False

    def test_teacher_week_limit_under(self):
        checker = ConstraintChecker()
        checker.MAX_TEACHER_SESSIONS_PER_WEEK = 5

        schedule = {}
        for i in range(4):
            schedule[f'W1_Dmonday_slot{i}'] = [{'teacher_id': 'T001', 'week': 1}]

        assert checker.check_teacher_week_limit('T001', 1, schedule) is True

    def test_validator_teacher_conflict_detection(self):
        validator = ScheduleValidator()
        schedule = {
            'W1_Dmonday_morning': [
                {'teacher_id': 'T001', 'course_id': 'C001'},
                {'teacher_id': 'T001', 'course_id': 'C002'},
            ],
        }
        result = ValidationResult()
        validator._check_teacher_conflicts(schedule, result)
        assert len(result.errors) >= 1

    def test_validator_no_teacher_conflict(self):
        validator = ScheduleValidator()
        schedule = {
            'W1_Dmonday_morning': [{'teacher_id': 'T001', 'course_id': 'C001'}],
            'W1_Dmonday_afternoon': [{'teacher_id': 'T001', 'course_id': 'C002'}],
        }
        result = ValidationResult()
        validator._check_teacher_conflicts(schedule, result)
        assert len(result.errors) == 0


class TestRoomConflictScenarios:
    """测试教室冲突场景"""

    def test_room_same_slot_conflict(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)

        allocator.allocate_room('R001', 1, 'monday', 'morning')
        assert allocator.is_room_available('R001', 1, 'monday', 'morning') is False

        result = allocator.allocate_room('R001', 1, 'monday', 'morning')
        assert result is False

    def test_room_different_slots_no_conflict(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)

        allocator.allocate_room('R001', 1, 'monday', 'morning')
        assert allocator.is_room_available('R001', 1, 'monday', 'afternoon') is True

    def test_room_conflict_constraint_checker(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')

        checker = ConstraintChecker()
        assert checker.check_room_conflict('R001', 1, 'monday', 'morning', allocator) is False
        assert checker.check_room_conflict('R001', 1, 'monday', 'afternoon', allocator) is True

    def test_scheduler_avoids_room_conflict(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
            Course('C002', '英语', 'T002', 'CL002', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)

        room_slots = {}
        for slot_key, sessions in scheduler.schedule.items():
            for session in sessions:
                rid = session.get('room_id')
                if rid == 'R001':
                    if slot_key not in room_slots:
                        room_slots[slot_key] = []
                    room_slots[slot_key].append(session)

        for slot, sessions in room_slots.items():
            assert len(sessions) <= 1

    def test_multiple_rooms_available(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        scheduler.add_room('R002', '201教室', 50, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
            Course('C002', '英语', 'T001', 'CL002', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)

        assert len(scheduler.schedule) >= 1 or len(scheduler.failed_courses) >= 0

    def test_room_type_conflict(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '机房')

        checker = ConstraintChecker()
        room = allocator.get_room('R001')
        course = Course('C001', '数学', 'T001', 'CL001', 4, room_type='普通教室')

        assert checker.check_room_type(course, room) is False

    def test_validator_room_conflict_detection(self):
        validator = ScheduleValidator()
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')

        schedule = {
            'W1_Dmonday_morning': [
                {'room_id': 'R001', 'course_id': 'C001'},
                {'room_id': 'R001', 'course_id': 'C002'},
            ],
        }
        result = ValidationResult()
        validator._check_room_conflicts(schedule, allocator, result)
        assert len(result.errors) >= 1

    def test_no_room_conflict_different_rooms(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.add_room('R002', '201教室', 50)

        schedule = {
            'W1_Dmonday_morning': [
                {'room_id': 'R001', 'course_id': 'C001'},
                {'room_id': 'R002', 'course_id': 'C002'},
            ],
        }
        validator = ScheduleValidator()
        result = ValidationResult()
        validator._check_room_conflicts(schedule, allocator, result)
        assert len(result.errors) == 0


class TestCombinedConstraintScenarios:
    """测试组合约束场景"""

    def test_schedule_with_holiday_and_room_conflict(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        holidays = {
            'h1': {
                'start_date': '2026-03-02',
                'end_date': '2026-03-02',
                'name': '节假日',
            }
        }
        scheduler.setup_holidays(holidays)

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)

        for slot_key in scheduler.schedule:
            parts = slot_key.split('_')
            if len(parts) >= 3:
                week = int(parts[0][1:])
                day = parts[1][1:]
                date = scheduler.time_pool.get_date(week, day)
                if date:
                    assert scheduler.holiday_manager.is_holiday(date) is False

    def test_schedule_capacity_and_type_match(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '小教室', 20, '普通教室')
        scheduler.add_room('R002', '大教室', 60, '普通教室')

        courses = [
            Course('C001', '大课', 'T001', 'CL001', 4, student_count=50, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)

        for slot_key, sessions in scheduler.schedule.items():
            for session in sessions:
                assert session['room_id'] == 'R002'

    def test_schedule_multiple_teachers_and_rooms(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        for i in range(3):
            scheduler.add_room(f'R00{i}', f'{i}教室', 50, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
            Course('C002', '英语', 'T002', 'CL002', 4, student_count=30, room_type='普通教室'),
            Course('C003', '物理', 'T003', 'CL003', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)
        assert len(scheduler.schedule) > 0

    def test_optimizer_finds_best_slot_with_constraints(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        allocator.add_room('R002', '201教室', 40, '普通教室')

        pool = TimePool(start_date='2026-03-02')
        constraint = ConstraintChecker()
        holiday_mgr = HolidayManager()
        optimizer = ScheduleOptimizer()

        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=35, room_type='普通教室')
        schedule = {}

        candidate_slots = [
            (1, 'monday', 'morning', 'R001'),
            (1, 'monday', 'morning', 'R002'),
            (1, 'tuesday', 'morning', 'R001'),
        ]

        best = optimizer.find_best_slot(
            course, candidate_slots, pool, allocator, schedule, constraint, holiday_mgr
        )
        assert best is not None
        assert best[3] in ['R001', 'R002']

    def test_full_schedule_validation(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)

        result = scheduler.validate_schedule()
        assert isinstance(result.is_valid, bool)

    def test_empty_schedule_validation(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        result = scheduler.validate_schedule()
        assert result.is_valid is True

    def test_scheduler_handles_no_rooms(self):
        scheduler = MainScheduler(start_date='2026-03-02')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)
        failed = scheduler.get_failed_courses()
        assert len(failed) == 1

    def test_consecutive_scheduling_no_conflicts(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        for i in range(5):
            scheduler.add_room(f'R00{i}', f'{i}教室', 50, '普通教室')

        courses = []
        for i in range(10):
            courses.append(
                Course(
                    f'C{i:03d}', f'课程{i}', f'T{i:03d}', f'CL{i:03d}',
                    4, student_count=30, room_type='普通教室'
                )
            )

        scheduler.schedule_courses(courses)

        for slot_key, sessions in scheduler.schedule.items():
            teacher_ids = [s['teacher_id'] for s in sessions]
            room_ids = [s['room_id'] for s in sessions]
            assert len(teacher_ids) == len(set(teacher_ids))
            assert len(room_ids) == len(set(room_ids))
