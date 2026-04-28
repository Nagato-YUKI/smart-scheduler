from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict


class ValidationResult:
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def to_dict(self) -> Dict:
        return {"is_valid": self.is_valid, "error_count": len(self.errors), "warning_count": len(self.warnings), "errors": self.errors, "warnings": self.warnings}


class ScheduleValidator:
    def __init__(self):
        self.max_teacher_sessions_per_week = 5
        self.max_class_sessions_per_day = 8

    def validate_schedule(self, schedule: Dict, courses: List, time_pool, room_allocator, holiday_manager) -> ValidationResult:
        result = ValidationResult()
        self._check_teacher_conflicts(schedule, result)
        self._check_room_conflicts(schedule, room_allocator, result)
        self._check_class_conflicts(schedule, result)
        self._check_holiday_conflicts(schedule, time_pool, holiday_manager, result)
        self._check_teacher_week_limit(schedule, result)
        self._check_class_daily_limit(schedule, result)
        self._check_all_courses_scheduled(schedule, courses, result)
        self._check_fixed_room_constraints(schedule, courses, result)
        return result

    def _check_teacher_conflicts(self, schedule: Dict, result: ValidationResult):
        teacher_slots = defaultdict(set)
        for slot_key, sessions in schedule.items():
            for session in sessions:
                teacher_id = session.get('teacher_id')
                if teacher_id:
                    if slot_key in teacher_slots[teacher_id]:
                        result.add_error(f"教师 {teacher_id} 在时段 {slot_key} 有课程冲突")
                    teacher_slots[teacher_id].add(slot_key)

    def _check_room_conflicts(self, schedule: Dict, room_allocator, result: ValidationResult):
        room_slots = defaultdict(set)
        for slot_key, sessions in schedule.items():
            for session in sessions:
                room_id = session.get('room_id')
                if room_id:
                    if slot_key in room_slots[room_id]:
                        result.add_error(f"教室 {room_id} 在时段 {slot_key} 有课程冲突")
                    room_slots[room_id].add(slot_key)

    def _check_class_conflicts(self, schedule: Dict, result: ValidationResult):
        class_slots = defaultdict(set)
        for slot_key, sessions in schedule.items():
            for session in sessions:
                class_id = session.get('class_id')
                if class_id:
                    if slot_key in class_slots[class_id]:
                        result.add_error(f"班级 {class_id} 在时段 {slot_key} 有课程冲突")
                    class_slots[class_id].add(slot_key)

    def _check_holiday_conflicts(self, schedule: Dict, time_pool, holiday_manager, result: ValidationResult):
        for slot_key, sessions in schedule.items():
            parts = slot_key.split("_")
            if len(parts) >= 3:
                week = int(parts[0][1:])
                day = parts[1][1:]
                date = time_pool.get_date(week, day)
                if date and holiday_manager.is_holiday(date):
                    result.add_error(f"时段 {slot_key} 安排在节假日 {date.strftime('%Y-%m-%d')}")

    def _check_teacher_week_limit(self, schedule: Dict, result: ValidationResult):
        teacher_week_sessions = defaultdict(lambda: defaultdict(int))
        for slot_key, sessions in schedule.items():
            for session in sessions:
                teacher_id = session.get('teacher_id')
                week = session.get('week')
                if teacher_id and week:
                    teacher_week_sessions[teacher_id][week] += 1
        for teacher_id, week_counts in teacher_week_sessions.items():
            for week, count in week_counts.items():
                if count > self.max_teacher_sessions_per_week:
                    result.add_error(f"教师 {teacher_id} 在周次 {week} 安排了 {count} 课时，超过上限")

    def _check_class_daily_limit(self, schedule: Dict, result: ValidationResult):
        class_day_sessions = defaultdict(lambda: defaultdict(int))
        for slot_key, sessions in schedule.items():
            for session in sessions:
                class_id = session.get('class_id')
                day = session.get('day')
                week = session.get('week')
                if class_id and day and week:
                    class_day_sessions[class_id][f"W{week}_D{day}"] += 1
        for class_id, day_counts in class_day_sessions.items():
            for day_key, count in day_counts.items():
                if count > self.max_class_sessions_per_day:
                    result.add_error(f"班级 {class_id} 在 {day_key} 安排了 {count} 课时，超过上限")

    def _check_all_courses_scheduled(self, schedule: Dict, courses: List, result: ValidationResult):
        scheduled_course_ids = set()
        for slot_key, sessions in schedule.items():
            for session in sessions:
                course_id = session.get('course_id')
                if course_id:
                    scheduled_course_ids.add(course_id)
        for course in courses:
            course_id = getattr(course, 'course_id', None)
            if course_id and course_id not in scheduled_course_ids:
                result.add_error(f"课程 {course_id} 未安排")

    def _check_fixed_room_constraints(self, schedule: Dict, courses: List, result: ValidationResult):
        course_map = {getattr(c, 'course_id', None): c for c in courses}
        for slot_key, sessions in schedule.items():
            for session in sessions:
                course_id = session.get('course_id')
                room_id = session.get('room_id')
                if course_id and course_id in course_map:
                    course = course_map[course_id]
                    fixed_room = getattr(course, 'fixed_room_id', None)
                    if fixed_room and room_id != fixed_room:
                        result.add_error(f"课程 {course_id} 应使用固定教室 {fixed_room}")
