from typing import Dict, List, Tuple, Optional, Set


class ConstraintChecker:
    MAX_TEACHER_SESSIONS_PER_WEEK = 5

    def __init__(self):
        self.violations = []

    def check_holiday_conflict(self, week: int, day: str, time_pool, holiday_manager) -> bool:
        date = time_pool.get_date(week, day)
        if date and holiday_manager.is_holiday(date):
            return False
        return True

    def check_fixed_room(self, course, room_id: str, room_allocator) -> bool:
        if not hasattr(course, 'fixed_room_id') or not course.fixed_room_id:
            return True
        return course.fixed_room_id == room_id

    def check_capacity(self, course, room) -> bool:
        required_capacity = getattr(course, 'student_count', 0)
        return room.capacity >= required_capacity

    def check_room_type(self, course, room) -> bool:
        required_type = getattr(course, 'room_type', 'normal')
        return room.room_type == required_type

    def check_teacher_week_limit(self, teacher_id: str, week: int, schedule: Dict) -> bool:
        count = 0
        for key, sessions in schedule.items():
            for session in sessions:
                if session.get('teacher_id') == teacher_id and session.get('week') == week:
                    count += 1

        return count < self.MAX_TEACHER_SESSIONS_PER_WEEK

    def check_teacher_conflict(self, teacher_id: str, week: int, day: str, period: str,
                               schedule: Dict) -> bool:
        slot_key = f"W{week}_D{day}_{period}"

        for key, sessions in schedule.items():
            for session in sessions:
                if (session.get('teacher_id') == teacher_id and
                        key == slot_key):
                    return False

        return True

    def check_room_conflict(self, room_id: str, week: int, day: str, period: str,
                            room_allocator) -> bool:
        return room_allocator.is_room_available(room_id, week, day, period)

    def check_class_conflict(self, class_id: str, week: int, day: str, period: str,
                             schedule: Dict) -> bool:
        slot_key = f"W{week}_D{day}_{period}"

        for key, sessions in schedule.items():
            for session in sessions:
                if (session.get('class_id') == class_id and
                        key == slot_key):
                    return False

        return True

    def check_time_slot_available(self, week: int, day: str, period: str, time_pool) -> bool:
        return time_pool.is_available(week, day, period)

    def check_all_hard_constraints(self, course, room_id: str, week: int, day: str,
                                   period: str, schedule: Dict, time_pool, room_allocator,
                                   holiday_manager) -> Tuple[bool, List[str]]:
        violations = []
        room = room_allocator.get_room(room_id)

        if room is None:
            violations.append(f"教室 {room_id} 不存在")
            return False, violations

        if not self.check_time_slot_available(week, day, period, time_pool):
            violations.append(f"时段 {week}/{day}/{period} 不可用")

        if not self.check_holiday_conflict(week, day, time_pool, holiday_manager):
            violations.append(f"时段 {week}/{day}/{period} 是节假日")

        if not self.check_fixed_room(course, room_id, room_allocator):
            violations.append(f"课程需要固定教室 {course.fixed_room_id}")

        if not self.check_capacity(course, room):
            violations.append(f"教室容量不足: {room.capacity} < {getattr(course, 'student_count', 0)}")

        if not self.check_room_type(course, room):
            violations.append(f"教室类型不匹配: {room.room_type} != {getattr(course, 'room_type', 'normal')}")

        teacher_id = getattr(course, 'teacher_id', None)
        if teacher_id:
            if not self.check_teacher_week_limit(teacher_id, week, schedule):
                violations.append(f"教师 {teacher_id} 在周次 {week} 课时已达上限")

            if not self.check_teacher_conflict(teacher_id, week, day, period, schedule):
                violations.append(f"教师 {teacher_id} 在时段 {week}/{day}/{period} 有冲突")

        if not self.check_room_conflict(room_id, week, day, period, room_allocator):
            violations.append(f"教室 {room_id} 在时段 {week}/{day}/{period} 有冲突")

        class_id = getattr(course, 'class_id', None)
        if class_id:
            if not self.check_class_conflict(class_id, week, day, period, schedule):
                violations.append(f"班级 {class_id} 在时段 {week}/{day}/{period} 有冲突")

        return len(violations) == 0, violations

    def clear_violations(self):
        self.violations = []
