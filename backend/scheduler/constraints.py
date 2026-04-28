from typing import Dict, List, Tuple, Set, Optional
from .time_pool import TimePool
from .room_allocator import RoomAllocator
from .holiday_manager import HolidayManager


class ConstraintChecker:
    def __init__(self):
        self.hard_constraints = [
            self._check_teacher_conflict,
            self._check_class_conflict,
            self._check_room_conflict,
            self._check_holiday_conflict,
            self._check_teacher_capacity,
            self._check_class_capacity,
            self._check_room_capacity,
            self._check_room_type_match,
            self._check_fixed_room,
            self._check_time_slot_availability,
        ]
        self.soft_constraints = [
            self._check_teacher_day_concentration,
            self._check_class_day_balance,
            self._check_period_preference,
        ]

    def check_all_hard_constraints(self, course, room_id: str, week: int, day: str,
                                   period: str, schedule: Dict, time_pool: TimePool,
                                   room_allocator: RoomAllocator, holiday_manager: HolidayManager) -> Tuple[bool, List[str]]:
        violations = []
        for constraint in self.hard_constraints:
            is_valid, violation_msg = constraint(course, room_id, week, day, period, schedule, time_pool, room_allocator, holiday_manager)
            if not is_valid:
                violations.append(violation_msg)
                return False, violations
        return True, []

    def check_soft_constraints(self, course, room_id: str, week: int, day: str,
                               period: str, schedule: Dict, time_pool: TimePool,
                               room_allocator: RoomAllocator, holiday_manager: HolidayManager) -> Tuple[float, List[str]]:
        total_score = 0.0
        warnings = []
        for constraint in self.soft_constraints:
            score, warning_msg = constraint(course, room_id, week, day, period, schedule, time_pool, room_allocator, holiday_manager)
            total_score += score
            if warning_msg:
                warnings.append(warning_msg)
        return total_score / len(self.soft_constraints), warnings

    def _check_teacher_conflict(self, course, room_id: str, week: int, day: str,
                                period: str, schedule: Dict, *args) -> Tuple[bool, str]:
        teacher_id = getattr(course, 'teacher_id', None)
        if not teacher_id:
            return True, ""
        slot_key = f"W{week}_D{day}_{period}"
        for key, sessions in schedule.items():
            if key == slot_key:
                for session in sessions:
                    if session.get('teacher_id') == teacher_id:
                        return False, f"教师 {teacher_id} 在 {slot_key} 有课程冲突"
        return True, ""

    def _check_class_conflict(self, course, room_id: str, week: int, day: str,
                              period: str, schedule: Dict, *args) -> Tuple[bool, str]:
        class_id = getattr(course, 'class_id', None)
        if not class_id:
            return True, ""
        slot_key = f"W{week}_D{day}_{period}"
        for key, sessions in schedule.items():
            if key == slot_key:
                for session in sessions:
                    if session.get('class_id') == class_id:
                        return False, f"班级 {class_id} 在 {slot_key} 有课程冲突"
        return True, ""

    def _check_room_conflict(self, course, room_id: str, week: int, day: str,
                             period: str, schedule: Dict, *args) -> Tuple[bool, str]:
        if not room_id:
            return True, ""
        slot_key = f"W{week}_D{day}_{period}"
        for key, sessions in schedule.items():
            if key == slot_key:
                for session in sessions:
                    if session.get('room_id') == room_id:
                        return False, f"教室 {room_id} 在 {slot_key} 有课程冲突"
        return True, ""

    def _check_holiday_conflict(self, course, room_id: str, week: int, day: str,
                                period: str, schedule: Dict, time_pool: TimePool,
                                room_allocator: RoomAllocator, holiday_manager: HolidayManager) -> Tuple[bool, str]:
        date_obj = time_pool.get_date(week, day)
        if date_obj and holiday_manager.is_holiday(date_obj):
            return False, f"{day} 是节假日 ({holiday_manager.get_holiday_name(date_obj)})"
        return True, ""

    def _check_teacher_capacity(self, course, room_id: str, week: int, day: str,
                                period: str, schedule: Dict, time_pool: TimePool, *args) -> Tuple[bool, str]:
        teacher_id = getattr(course, 'teacher_id', None)
        if not teacher_id:
            return True, ""
        if not time_pool.check_teacher_capacity(teacher_id, week, day):
            return False, f"教师 {teacher_id} 在 {week}/{day} 已达每日最大课时"
        return True, ""

    def _check_class_capacity(self, course, room_id: str, week: int, day: str,
                              period: str, schedule: Dict, time_pool: TimePool, *args) -> Tuple[bool, str]:
        class_id = getattr(course, 'class_id', None)
        if not class_id:
            return True, ""
        if not time_pool.check_class_capacity(class_id, week, day):
            return False, f"班级 {class_id} 在 {week}/{day} 已达每日最大课时"
        return True, ""

    def _check_room_capacity(self, course, room_id: str, week: int, day: str,
                             period: str, schedule: Dict, time_pool: TimePool,
                             room_allocator: RoomAllocator, *args) -> Tuple[bool, str]:
        if not room_id:
            return True, ""
        if not room_allocator.is_room_available(room_id, week, day, period):
            return False, f"教室 {room_id} 在 {week}/{day}/{period} 已被占用"
        return True, ""

    def _check_room_type_match(self, course, room_id: str, week: int, day: str,
                               period: str, schedule: Dict, time_pool: TimePool,
                               room_allocator: RoomAllocator, *args) -> Tuple[bool, str]:
        if not room_id:
            return True, ""
        room = room_allocator.get_room(room_id)
        required_type = getattr(course, 'room_type', 'normal')
        if room and room.room_type != required_type and required_type != 'normal':
            if room.room_type == 'normal':
                pass
            else:
                return False, f"教室 {room_id} 类型 {room.room_type} 不匹配课程要求 {required_type}"
        return True, ""

    def _check_fixed_room(self, course, room_id: str, week: int, day: str,
                          period: str, schedule: Dict, *args) -> Tuple[bool, str]:
        fixed_room_id = getattr(course, 'fixed_room_id', None)
        if fixed_room_id and room_id != fixed_room_id:
            return False, f"课程要求固定教室 {fixed_room_id}，但尝试分配到 {room_id}"
        return True, ""

    def _check_time_slot_availability(self, course, room_id: str, week: int, day: str,
                                      period: str, schedule: Dict, time_pool: TimePool, *args) -> Tuple[bool, str]:
        if not time_pool.is_available(week, day, period):
            return False, f"时段 {week}/{day}/{period} 不可用"
        return True, ""

    def _check_teacher_day_concentration(self, course, room_id: str, week: int, day: str, period: str, schedule: Dict, *args) -> Tuple[float, str]:
        teacher_id = getattr(course, 'teacher_id', None)
        if not teacher_id:
            return 1.0, ""
        teacher_days = set()
        for key, sessions in schedule.items():
            for session in sessions:
                if session.get('teacher_id') == teacher_id:
                    parts = key.split('_')
                    if len(parts) >= 2:
                        teacher_days.add(parts[1])
        if day in teacher_days:
            return 1.0, ""
        if len(teacher_days) >= 4:
            return 0.3, f"教师 {teacher_id} 已在一周 {len(teacher_days)} 天有课"
        return 0.8, ""

    def _check_class_day_balance(self, course, room_id: str, week: int, day: str,
                                 period: str, schedule: Dict, *args) -> Tuple[float, str]:
        class_id = getattr(course, 'class_id', None)
        if not class_id:
            return 1.0, ""
        class_day_courses = 0
        for key, sessions in schedule.items():
            parts = key.split('_')
            if len(parts) >= 2 and parts[1] == f"D{day}":
                for session in sessions:
                    if session.get('class_id') == class_id:
                        class_day_courses += 1
        if class_day_courses >= 3:
            return 0.5, f"班级 {class_id} 在 {day} 已有 {class_day_courses} 节课"
        return 1.0, ""

    def _check_period_preference(self, course, room_id: str, week: int, day: str,
                                 period: str, schedule: Dict, *args) -> Tuple[float, str]:
        preferred_periods = getattr(course, 'preferred_periods', ["morning", "afternoon", "evening"])
        if period in preferred_periods:
            return 1.0, ""
        return 0.5, f"时段 {period} 不是课程首选"
