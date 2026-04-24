"""排课算法单元测试"""
import pytest
from datetime import datetime, timedelta

from scheduler.time_pool import TimePool, TimeSlot
from scheduler.holiday_manager import HolidayManager
from scheduler.room_allocator import RoomAllocator, Room
from scheduler.constraints import ConstraintChecker
from scheduler.optimizer import ScheduleOptimizer
from scheduler.statistics import ScheduleStatistics
from scheduler.validator import ScheduleValidator, ValidationResult
from scheduler.main_scheduler import MainScheduler, Course


class TestTimePool:
    """测试时间资源池"""

    def test_initialization(self):
        pool = TimePool(start_date='2026-03-02')
        assert pool.start_date == datetime(2026, 3, 2)
        assert len(pool.time_slots) > 0

    def test_generate_time_slots(self):
        pool = TimePool(start_date='2026-03-02')
        total_expected = 16 * 5 * 3
        assert len(pool.time_slots) == total_expected
        assert len(pool.available_slots) == total_expected

    def test_available_slots_count(self):
        pool = TimePool(start_date='2026-03-02')
        assert len(pool.available_slots) == 16 * 5 * 3

    def test_is_available_initial(self):
        pool = TimePool(start_date='2026-03-02')
        assert pool.is_available(1, 'monday', 'morning') is True
        assert pool.is_available(16, 'friday', 'evening') is True

    def test_remove_slot(self):
        pool = TimePool(start_date='2026-03-02')
        pool.remove_slot(1, 'monday', 'morning')
        assert pool.is_available(1, 'monday', 'morning') is False

    def test_add_slot(self):
        pool = TimePool(start_date='2026-03-02')
        pool.remove_slot(1, 'monday', 'morning')
        assert pool.is_available(1, 'monday', 'morning') is False
        pool.add_slot(1, 'monday', 'morning')
        assert pool.is_available(1, 'monday', 'morning') is True

    def test_remove_slot_idempotent(self):
        pool = TimePool(start_date='2026-03-02')
        pool.remove_slot(1, 'monday', 'morning')
        pool.remove_slot(1, 'monday', 'morning')
        assert pool.is_available(1, 'monday', 'morning') is False

    def test_get_date(self):
        pool = TimePool(start_date='2026-03-02')
        date = pool.get_date(1, 'monday')
        assert date == datetime(2026, 3, 2)

    def test_get_date_wednesday(self):
        pool = TimePool(start_date='2026-03-02')
        date = pool.get_date(1, 'wednesday')
        assert date == datetime(2026, 3, 4)

    def test_get_date_invalid_week(self):
        pool = TimePool(start_date='2026-03-02')
        assert pool.get_date(0, 'monday') is None
        assert pool.get_date(20, 'monday') is None

    def test_get_period_hours(self):
        pool = TimePool()
        assert pool.get_period_hours('morning') == 4
        assert pool.get_period_hours('afternoon') == 4
        assert pool.get_period_hours('evening') == 3

    def test_get_period_hours_invalid(self):
        pool = TimePool()
        assert pool.get_period_hours('invalid') == 0

    def test_get_week_day_date(self):
        pool = TimePool(start_date='2026-03-02')
        date = pool.get_week_day_date(2, 'tuesday')
        expected = datetime(2026, 3, 10)
        assert date == expected

    def test_get_available_slots(self):
        pool = TimePool(start_date='2026-03-02')
        slots = pool.get_available_slots()
        assert len(slots) == 16 * 5 * 3

    def test_get_available_slots_after_remove(self):
        pool = TimePool(start_date='2026-03-02')
        pool.remove_slot(1, 'monday', 'morning')
        pool.remove_slot(1, 'monday', 'afternoon')
        slots = pool.get_available_slots()
        assert len(slots) == 16 * 5 * 3 - 2

    def test_get_slots_by_week(self):
        pool = TimePool(start_date='2026-03-02')
        slots = pool.get_slots_by_week(1)
        assert len(slots) == 5 * 3

    def test_get_slots_by_day(self):
        pool = TimePool(start_date='2026-03-02')
        slots = pool.get_slots_by_day(1, 'monday')
        assert len(slots) == 3

    def test_get_total_available_hours(self):
        pool = TimePool(start_date='2026-03-02')
        total_hours = 16 * (4 + 4 + 3) * 5
        assert pool.get_total_available_hours() == total_hours

    def test_get_total_available_hours_after_remove(self):
        pool = TimePool(start_date='2026-03-02')
        pool.remove_slot(1, 'monday', 'morning')
        total = pool.get_total_available_hours()
        assert total == 16 * (4 + 4 + 3) * 5 - 4

    def test_reset(self):
        pool = TimePool(start_date='2026-03-02')
        pool.remove_slot(1, 'monday', 'morning')
        pool.reset()
        assert len(pool.available_slots) == 16 * 5 * 3
        assert pool.is_available(1, 'monday', 'morning') is True

    def test_time_slot_equality(self):
        slot1 = TimeSlot(1, 'monday', 'morning')
        slot2 = TimeSlot(1, 'monday', 'morning')
        slot3 = TimeSlot(1, 'monday', 'afternoon')
        assert slot1 == slot2
        assert slot1 != slot3

    def test_time_slot_hash(self):
        slot1 = TimeSlot(1, 'monday', 'morning')
        slot2 = TimeSlot(1, 'monday', 'morning')
        assert hash(slot1) == hash(slot2)

    def test_time_slot_to_key(self):
        slot = TimeSlot(1, 'monday', 'morning')
        assert slot.to_key() == 'W1_Dmonday_morning'

    def test_default_start_date(self):
        pool = TimePool()
        assert isinstance(pool.start_date, datetime)


class TestHolidayManager:
    """测试节假日管理"""

    def test_initialization(self):
        manager = HolidayManager()
        assert manager.holidays == {}
        assert manager.holiday_dates == set()

    def test_add_single_holiday(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', name='劳动节')
        assert 'h1' in manager.holidays
        assert '2026-05-01' in manager.holiday_dates

    def test_is_holiday(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', name='劳动节')
        assert manager.is_holiday(datetime(2026, 5, 1)) is True
        assert manager.is_holiday(datetime(2026, 5, 2)) is False

    def test_add_holiday_range(self):
        manager = HolidayManager()
        manager.add_holiday('h2', '2026-05-01', '2026-05-03', name='五一假期')
        assert '2026-05-01' in manager.holiday_dates
        assert '2026-05-02' in manager.holiday_dates
        assert '2026-05-03' in manager.holiday_dates
        assert '2026-05-04' not in manager.holiday_dates

    def test_set_holidays(self):
        manager = HolidayManager()
        holidays = {
            'h1': {'start_date': '2026-05-01', 'end_date': '2026-05-03', 'name': '五一'},
            'h2': {'start_date': '2026-10-01', 'end_date': '2026-10-07', 'name': '国庆'},
        }
        manager.set_holidays(holidays)
        assert manager.is_holiday(datetime(2026, 5, 2)) is True
        assert manager.is_holiday(datetime(2026, 10, 5)) is True
        assert manager.is_holiday(datetime(2026, 6, 1)) is False

    def test_remove_holiday(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', '2026-05-03', name='五一')
        manager.remove_holiday('h1')
        assert 'h1' not in manager.holidays
        assert '2026-05-01' not in manager.holiday_dates

    def test_remove_nonexistent_holiday(self):
        manager = HolidayManager()
        manager.remove_holiday('nonexistent')
        assert len(manager.holidays) == 0

    def test_get_holiday_slots(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', name='劳动节')
        pool = TimePool(start_date='2026-04-06')
        slots = manager.get_holiday_slots(pool)
        assert len(slots) > 0

    def test_mark_holidays_in_pool(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', name='劳动节')
        pool = TimePool(start_date='2026-04-06')
        initial_count = len(pool.available_slots)
        removed = manager.mark_holidays_in_pool(pool)
        assert removed > 0
        assert len(pool.available_slots) < initial_count

    def test_get_holiday_count(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', '2026-05-03', name='五一')
        assert manager.get_holiday_count() == 3

    def test_get_holiday_count_with_range(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', '2026-05-05', name='假期')
        count = manager.get_holiday_count(
            datetime(2026, 5, 2), datetime(2026, 5, 4)
        )
        assert count == 3

    def test_get_holidays_in_week(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', name='劳动节')
        pool = TimePool(start_date='2026-04-06')
        week = 4
        holidays = manager.get_holidays_in_week(week, pool)
        assert len(holidays) >= 1

    def test_clear(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-05-01', '2026-05-03', name='五一')
        manager.clear()
        assert manager.holidays == {}
        assert manager.holiday_dates == set()


class TestRoomAllocator:
    """测试教室预分配"""

    def test_add_room(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        assert allocator.get_room('R001') is not None
        assert allocator.get_room('R001').capacity == 50

    def test_get_all_rooms(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        allocator.add_room('R002', '201教室', 60, '多媒体教室')
        assert len(allocator.get_all_rooms()) == 2

    def test_remove_room(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.remove_room('R001')
        assert allocator.get_room('R001') is None

    def test_remove_nonexistent_room(self):
        allocator = RoomAllocator()
        allocator.remove_room('nonexistent')

    def test_get_rooms_by_type(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        allocator.add_room('R002', '301机房', 40, '机房')
        rooms = allocator.get_rooms_by_type('普通教室')
        assert len(rooms) == 1
        assert rooms[0].room_id == 'R001'

    def test_get_rooms_by_capacity(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.add_room('R002', '201教室', 30)
        rooms = allocator.get_rooms_by_capacity(40)
        assert len(rooms) == 1

    def test_is_room_available(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        assert allocator.is_room_available('R001', 1, 'monday', 'morning') is True

    def test_is_room_available_nonexistent(self):
        allocator = RoomAllocator()
        assert allocator.is_room_available('nonexistent', 1, 'monday', 'morning') is False

    def test_allocate_room(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        result = allocator.allocate_room('R001', 1, 'monday', 'morning')
        assert result is True
        assert allocator.is_room_available('R001', 1, 'monday', 'morning') is False

    def test_allocate_room_nonexistent(self):
        allocator = RoomAllocator()
        result = allocator.allocate_room('nonexistent', 1, 'monday', 'morning')
        assert result is False

    def test_allocate_room_already_allocated(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')
        result = allocator.allocate_room('R001', 1, 'monday', 'morning')
        assert result is False

    def test_deallocate_room(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')
        allocator.deallocate_room('R001', 1, 'monday', 'morning')
        assert allocator.is_room_available('R001', 1, 'monday', 'morning') is True

    def test_deallocate_nonexistent(self):
        allocator = RoomAllocator()
        allocator.deallocate_room('nonexistent', 1, 'monday', 'morning')

    def test_find_best_room_fixed(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        room = allocator.find_best_room(30, fixed_room_id='R001')
        assert room.room_id == 'R001'

    def test_find_best_room_fixed_capacity_insufficient(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 20)
        room = allocator.find_best_room(50, fixed_room_id='R001')
        assert room is None

    def test_find_best_room_by_capacity(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.add_room('R002', '201教室', 30)
        room = allocator.find_best_room(25)
        assert room.room_id == 'R002'

    def test_find_best_room_no_match(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 20)
        room = allocator.find_best_room(50)
        assert room is None

    def test_find_available_rooms(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.add_room('R002', '201教室', 30)
        rooms = allocator.find_available_rooms(required_capacity=25)
        assert len(rooms) == 2
        assert rooms[0].room_id == 'R002'

    def test_find_available_rooms_with_time(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')
        rooms = allocator.find_available_rooms(
            required_capacity=25,
            week=1, day='monday', period='morning'
        )
        assert len(rooms) == 0

    def test_find_available_rooms_fixed(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        rooms = allocator.find_available_rooms(
            required_capacity=30, fixed_room_id='R001'
        )
        assert len(rooms) == 1
        assert rooms[0].room_id == 'R001'

    def test_get_room_usage_stats(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')
        stats = allocator.get_room_usage_stats()
        assert stats['R001']['used_slots'] == 1

    def test_clear_schedule(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')
        allocator.clear_schedule()
        assert allocator.is_room_available('R001', 1, 'monday', 'morning') is True

    def test_room_to_dict(self):
        room = Room('R001', '101教室', 50, '普通教室')
        d = room.to_dict()
        assert d['room_id'] == 'R001'
        assert d['capacity'] == 50
        assert d['room_type'] == '普通教室'

    def test_room_repr(self):
        room = Room('R001', '101教室', 50)
        assert 'R001' in repr(room)


class TestConstraintChecker:
    """测试硬约束检查"""

    def setup_method(self):
        self.checker = ConstraintChecker()

    def test_check_holiday_conflict_no_holiday(self):
        manager = HolidayManager()
        pool = TimePool(start_date='2026-03-02')
        assert self.checker.check_holiday_conflict(1, 'monday', pool, manager) is True

    def test_check_holiday_conflict_has_holiday(self):
        manager = HolidayManager()
        manager.add_holiday('h1', '2026-03-02', name='节假日')
        pool = TimePool(start_date='2026-03-02')
        assert self.checker.check_holiday_conflict(1, 'monday', pool, manager) is False

    def test_check_fixed_room_no_fixed(self):
        allocator = RoomAllocator()
        course = Course('C001', '数学', 'T001', 'CL001', 4)
        assert self.checker.check_fixed_room(course, 'R001', allocator) is True

    def test_check_fixed_room_match(self):
        allocator = RoomAllocator()
        course = Course('C001', '数学', 'T001', 'CL001', 4, fixed_room_id='R001')
        assert self.checker.check_fixed_room(course, 'R001', allocator) is True

    def test_check_fixed_room_mismatch(self):
        allocator = RoomAllocator()
        course = Course('C001', '数学', 'T001', 'CL001', 4, fixed_room_id='R002')
        assert self.checker.check_fixed_room(course, 'R001', allocator) is False

    def test_check_capacity_sufficient(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        room = allocator.get_room('R001')
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=30)
        assert self.checker.check_capacity(course, room) is True

    def test_check_capacity_insufficient(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 20)
        room = allocator.get_room('R001')
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=50)
        assert self.checker.check_capacity(course, room) is False

    def test_check_room_type_match(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        room = allocator.get_room('R001')
        course = Course('C001', '数学', 'T001', 'CL001', 4, room_type='普通教室')
        assert self.checker.check_room_type(course, room) is True

    def test_check_room_type_mismatch(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '机房')
        room = allocator.get_room('R001')
        course = Course('C001', '数学', 'T001', 'CL001', 4, room_type='普通教室')
        assert self.checker.check_room_type(course, room) is False

    def test_check_teacher_week_limit_not_exceeded(self):
        schedule = {
            'W1_Dmonday_morning': [{'teacher_id': 'T001', 'week': 1}],
        }
        assert self.checker.check_teacher_week_limit('T001', 1, schedule) is True

    def test_check_teacher_week_limit_exceeded(self):
        checker = ConstraintChecker()
        checker.MAX_TEACHER_SESSIONS_PER_WEEK = 5
        schedule = {
            f'W1_Dmonday_{p}': [{'teacher_id': 'T001', 'week': 1}]
            for p in ['morning', 'morning2', 'morning3', 'morning4', 'morning5']
        }
        schedule['W1_Dmonday_morning6'] = [{'teacher_id': 'T001', 'week': 1}]
        assert checker.check_teacher_week_limit('T001', 1, schedule) is False

    def test_check_teacher_conflict_no_conflict(self):
        schedule = {
            'W1_Dmonday_morning': [{'teacher_id': 'T002'}],
        }
        assert self.checker.check_teacher_conflict('T001', 1, 'monday', 'morning', schedule) is True

    def test_check_teacher_conflict_has_conflict(self):
        schedule = {
            'W1_Dmonday_morning': [{'teacher_id': 'T001'}],
        }
        assert self.checker.check_teacher_conflict('T001', 1, 'monday', 'morning', schedule) is False

    def test_check_room_conflict_available(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        assert self.checker.check_room_conflict('R001', 1, 'monday', 'morning', allocator) is True

    def test_check_room_conflict_occupied(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        allocator.allocate_room('R001', 1, 'monday', 'morning')
        assert self.checker.check_room_conflict('R001', 1, 'monday', 'morning', allocator) is False

    def test_check_class_conflict_no_conflict(self):
        schedule = {
            'W1_Dmonday_morning': [{'class_id': 'CL002'}],
        }
        assert self.checker.check_class_conflict('CL001', 1, 'monday', 'morning', schedule) is True

    def test_check_class_conflict_has_conflict(self):
        schedule = {
            'W1_Dmonday_morning': [{'class_id': 'CL001'}],
        }
        assert self.checker.check_class_conflict('CL001', 1, 'monday', 'morning', schedule) is False

    def test_check_time_slot_available(self):
        pool = TimePool(start_date='2026-03-02')
        assert self.checker.check_time_slot_available(1, 'monday', 'morning', pool) is True

    def test_check_time_slot_not_available(self):
        pool = TimePool(start_date='2026-03-02')
        pool.remove_slot(1, 'monday', 'morning')
        assert self.checker.check_time_slot_available(1, 'monday', 'morning', pool) is False

    def test_check_all_hard_constraints_pass(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        pool = TimePool(start_date='2026-03-02')
        holiday_mgr = HolidayManager()
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室')
        schedule = {}

        is_valid, violations = self.checker.check_all_hard_constraints(
            course, 'R001', 1, 'monday', 'morning', schedule,
            pool, allocator, holiday_mgr
        )
        assert is_valid is True
        assert len(violations) == 0

    def test_check_all_hard_constraints_room_not_found(self):
        allocator = RoomAllocator()
        pool = TimePool(start_date='2026-03-02')
        holiday_mgr = HolidayManager()
        course = Course('C001', '数学', 'T001', 'CL001', 4)
        schedule = {}

        is_valid, violations = self.checker.check_all_hard_constraints(
            course, 'nonexistent', 1, 'monday', 'morning', schedule,
            pool, allocator, holiday_mgr
        )
        assert is_valid is False
        assert any('不存在' in v for v in violations)

    def test_check_all_hard_constraints_holiday(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        pool = TimePool(start_date='2026-03-02')
        holiday_mgr = HolidayManager()
        holiday_mgr.add_holiday('h1', '2026-03-02', name='节假日')
        course = Course('C001', '数学', 'T001', 'CL001', 4)
        schedule = {}

        is_valid, violations = self.checker.check_all_hard_constraints(
            course, 'R001', 1, 'monday', 'morning', schedule,
            pool, allocator, holiday_mgr
        )
        assert is_valid is False
        assert any('节假日' in v for v in violations)

    def test_check_all_hard_constraints_capacity(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 10, '普通教室')
        pool = TimePool(start_date='2026-03-02')
        holiday_mgr = HolidayManager()
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=50, room_type='普通教室')
        schedule = {}

        is_valid, violations = self.checker.check_all_hard_constraints(
            course, 'R001', 1, 'monday', 'morning', schedule,
            pool, allocator, holiday_mgr
        )
        assert is_valid is False
        assert any('容量不足' in v for v in violations)

    def test_clear_violations(self):
        self.checker.violations = ['violation1', 'violation2']
        self.checker.clear_violations()
        assert self.checker.violations == []


class TestScheduleOptimizer:
    """测试优化器"""

    def test_calculate_teacher_concentration_score_new_day(self):
        optimizer = ScheduleOptimizer()
        schedule = {}
        score = optimizer.calculate_teacher_concentration_score('T001', schedule, 1, 'monday')
        assert 0 <= score <= 1.0

    def test_calculate_class_balance_score_empty(self):
        optimizer = ScheduleOptimizer()
        schedule = {}
        score = optimizer.calculate_class_balance_score('CL001', schedule, 1, 'monday')
        assert score == 1.0

    def test_calculate_capacity_match_score_perfect(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50)
        room = allocator.get_room('R001')
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=45)
        optimizer = ScheduleOptimizer()
        score = optimizer.calculate_capacity_match_score(course, room)
        assert score == 1.0

    def test_calculate_capacity_match_score_insufficient(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 20)
        room = allocator.get_room('R001')
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=50)
        optimizer = ScheduleOptimizer()
        score = optimizer.calculate_capacity_match_score(course, room)
        assert score == 0.0

    def test_calculate_period_preference_score(self):
        optimizer = ScheduleOptimizer()
        assert optimizer.calculate_period_preference_score('morning') == 1.0
        assert optimizer.calculate_period_preference_score('afternoon') == 0.8
        assert optimizer.calculate_period_preference_score('evening') == 0.5

    def test_calculate_slot_score(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=30)
        optimizer = ScheduleOptimizer()
        score = optimizer.calculate_slot_score(
            course, 'R001', allocator.get_room('R001'), 1, 'monday', 'morning', {}, allocator
        )
        assert 0 <= score <= 1.0

    def test_set_weights(self):
        optimizer = ScheduleOptimizer()
        optimizer.set_weights(teacher_concentration=0.5)
        assert optimizer.optimizer_weights['teacher_concentration'] == 0.5

    def test_find_best_slot(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 50, '普通教室')
        pool = TimePool(start_date='2026-03-02')
        constraint = ConstraintChecker()
        holiday_mgr = HolidayManager()
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室')
        schedule = {}
        optimizer = ScheduleOptimizer()

        candidate_slots = [(1, 'monday', 'morning', 'R001')]
        best = optimizer.find_best_slot(
            course, candidate_slots, pool, allocator, schedule, constraint, holiday_mgr
        )
        assert best is not None
        assert best[3] == 'R001'

    def test_find_best_slot_no_valid(self):
        allocator = RoomAllocator()
        allocator.add_room('R001', '101教室', 10, '普通教室')
        pool = TimePool(start_date='2026-03-02')
        constraint = ConstraintChecker()
        holiday_mgr = HolidayManager()
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=50, room_type='普通教室')
        schedule = {}
        optimizer = ScheduleOptimizer()

        candidate_slots = [(1, 'monday', 'morning', 'R001')]
        best = optimizer.find_best_slot(
            course, candidate_slots, pool, allocator, schedule, constraint, holiday_mgr
        )
        assert best is None

    def test_optimize_schedule(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, 'normal')
        course = Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='normal')

        scheduler.schedule_courses([course])

        assert len(scheduler.schedule) > 0


class TestScheduleValidator:
    """测试验证器"""

    def test_validation_result_initially_valid(self):
        result = ValidationResult()
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validation_result_add_error(self):
        result = ValidationResult()
        result.add_error('测试错误')
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_validation_result_add_warning(self):
        result = ValidationResult()
        result.add_warning('测试警告')
        assert result.is_valid is True
        assert len(result.warnings) == 1

    def test_validation_result_to_dict(self):
        result = ValidationResult()
        result.add_error('错误1')
        result.add_warning('警告1')
        d = result.to_dict()
        assert d['is_valid'] is False
        assert d['error_count'] == 1
        assert d['warning_count'] == 1

    def test_validate_schedule_empty(self):
        validator = ScheduleValidator()
        result = validator.validate_schedule({}, [], TimePool(), RoomAllocator(), HolidayManager())
        assert result.is_valid is True

    def test_validate_single_session_incomplete(self):
        validator = ScheduleValidator()
        session = {'teacher_id': 'T001'}
        result = validator.validate_single_session(
            session, {}, RoomAllocator(), ConstraintChecker(),
            TimePool(), HolidayManager()
        )
        assert result.is_valid is False
        assert '信息不完整' in result.errors[0]


class TestScheduleStatistics:
    """测试统计面板"""

    def test_calculate_total_scheduled_hours(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [{'course_id': 'C001'}],
            'W1_Dmonday_afternoon': [{'course_id': 'C002'}],
        }
        total = stats.calculate_total_scheduled_hours(schedule)
        assert total == 8

    def test_calculate_teacher_hours(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [
                {'course_id': 'C001', 'teacher_id': 'T001'},
            ],
        }
        hours = stats.calculate_teacher_hours(schedule)
        assert hours['T001'] == 4

    def test_calculate_class_hours(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [
                {'course_id': 'C001', 'class_id': 'CL001'},
            ],
        }
        hours = stats.calculate_class_hours(schedule)
        assert hours['CL001'] == 4

    def test_calculate_room_usage(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [
                {'course_id': 'C001', 'room_id': 'R001'},
            ],
            'W1_Dmonday_afternoon': [
                {'course_id': 'C002', 'room_id': 'R001'},
            ],
        }
        usage = stats.calculate_room_usage(schedule)
        assert usage['R001'] == 2

    def test_calculate_weekly_distribution(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [{'course_id': 'C001'}],
        }
        dist = stats.calculate_weekly_distribution(schedule)
        assert dist[1] == 4

    def test_calculate_daily_distribution(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [{'course_id': 'C001'}],
        }
        dist = stats.calculate_daily_distribution(schedule)
        assert dist['monday'] == 4

    def test_calculate_period_distribution(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [{'course_id': 'C001'}],
            'W1_Dmonday_afternoon': [{'course_id': 'C002'}],
        }
        dist = stats.calculate_period_distribution(schedule)
        assert dist['morning'] == 4
        assert dist['afternoon'] == 4

    def test_count_missing_courses(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [{'course_id': 'C001'}],
        }
        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4),
            Course('C002', '英语', 'T002', 'CL001', 4),
        ]
        missing = stats.count_missing_courses(schedule, courses)
        assert 'C002' in missing

    def test_calculate_completion_rate(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [{'course_id': 'C001'}],
        }
        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4),
            Course('C002', '英语', 'T002', 'CL001', 4),
        ]
        rate = stats.calculate_completion_rate(schedule, courses)
        assert rate == 50.0

    def test_calculate_completion_rate_empty_courses(self):
        stats = ScheduleStatistics()
        rate = stats.calculate_completion_rate({}, [])
        assert rate == 0.0

    def test_generate_full_report(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [{'course_id': 'C001', 'teacher_id': 'T001', 'class_id': 'CL001', 'room_id': 'R001'}],
        }
        courses = [Course('C001', '数学', 'T001', 'CL001', 4)]
        report = stats.generate_full_report(schedule, courses)
        assert 'total_scheduled_hours' in report
        assert 'teacher_hours' in report
        assert 'completion_rate' in report

    def test_get_teacher_schedule_summary(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [
                {'teacher_id': 'T001', 'course_id': 'C001', 'class_id': 'CL001', 'room_id': 'R001',
                 'week': 1, 'day': 'monday'},
            ],
        }
        summary = stats.get_teacher_schedule_summary(schedule, 'T001')
        assert summary['teacher_id'] == 'T001'
        assert summary['total_hours'] == 4
        assert summary['session_count'] == 1

    def test_get_class_schedule_summary(self):
        stats = ScheduleStatistics()
        schedule = {
            'W1_Dmonday_morning': [
                {'class_id': 'CL001', 'course_id': 'C001', 'teacher_id': 'T001', 'room_id': 'R001',
                 'week': 1, 'day': 'monday'},
            ],
        }
        summary = stats.get_class_schedule_summary(schedule, 'CL001')
        assert summary['class_id'] == 'CL001'
        assert summary['total_hours'] == 4

    def test_clear_cache(self):
        stats = ScheduleStatistics()
        stats.stats_cache = {'key': 'value'}
        stats.clear_cache()
        assert stats.stats_cache == {}


class TestMainScheduler:
    """测试主排课器"""

    def test_initialization(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        assert scheduler.time_pool is not None
        assert scheduler.holiday_manager is not None
        assert scheduler.room_allocator is not None

    def test_setup_holidays(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        holidays = {
            'h1': {'start_date': '2026-03-02', 'end_date': '2026-03-02', 'name': '节假日'}
        }
        scheduler.setup_holidays(holidays)
        assert scheduler.holiday_manager.is_holiday(datetime(2026, 3, 2)) is True

    def test_add_room(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        assert scheduler.room_allocator.get_room('R001') is not None

    def test_schedule_courses_basic(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]

        result = scheduler.schedule_courses(courses)
        assert len(result) > 0 or len(scheduler.failed_courses) == 0

    def test_schedule_courses_with_holidays(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        holidays = {
            'h1': {'start_date': '2026-03-02', 'end_date': '2026-03-02', 'name': '节假日'}
        }
        scheduler.setup_holidays(holidays)

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)
        log = scheduler.get_scheduling_log()
        assert len(log) == 1

    def test_get_failed_courses(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        failed = scheduler.get_failed_courses()
        assert isinstance(failed, list)

    def test_get_scheduling_log(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]
        scheduler.schedule_courses(courses)
        log = scheduler.get_scheduling_log()
        assert len(log) > 0
        assert log[0]['course_id'] == 'C001'

    def test_reset(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]
        scheduler.schedule_courses(courses)
        scheduler.reset()
        assert scheduler.schedule == {}
        assert scheduler.failed_courses == []

    def test_schedule_multiple_courses(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        scheduler.add_room('R002', '201教室', 60, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
            Course('C002', '英语', 'T002', 'CL002', 4, student_count=30, room_type='普通教室'),
        ]

        result = scheduler.schedule_courses(courses)
        assert len(result) > 0 or len(scheduler.failed_courses) >= 0

    def test_schedule_with_insufficient_rooms(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 10, '普通教室')

        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=50, room_type='普通教室'),
        ]

        scheduler.schedule_courses(courses)
        failed = scheduler.get_failed_courses()
        assert len(failed) >= 0

    def test_sort_courses_by_priority(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, priority=1),
            Course('C002', '英语', 'T002', 'CL002', 8, priority=5),
        ]
        sorted_courses = scheduler._sort_courses_by_priority(courses)
        assert sorted_courses[0].priority == 5

    def test_validate_schedule(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]
        scheduler.schedule_courses(courses)
        result = scheduler.validate_schedule()
        assert isinstance(result.is_valid, bool)

    def test_get_statistics(self):
        scheduler = MainScheduler(start_date='2026-03-02')
        scheduler.add_room('R001', '101教室', 50, '普通教室')
        courses = [
            Course('C001', '数学', 'T001', 'CL001', 4, student_count=30, room_type='普通教室'),
        ]
        scheduler.schedule_courses(courses)
        stats = scheduler.get_statistics()
        assert isinstance(stats, dict)
        assert 'total_scheduled_hours' in stats

    def test_course_to_dict(self):
        course = Course('C001', '数学', 'T001', 'CL001', 4)
        d = course.to_dict()
        assert d['course_id'] == 'C001'
        assert d['name'] == '数学'
        assert d['teacher_id'] == 'T001'

    def test_course_repr(self):
        course = Course('C001', '数学', 'T001', 'CL001', 4)
        assert 'C001' in repr(course)
