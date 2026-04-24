from typing import Dict, List, Optional, Tuple
from .time_pool import TimePool
from .holiday_manager import HolidayManager
from .room_allocator import RoomAllocator
from .constraints import ConstraintChecker
from .optimizer import ScheduleOptimizer
from .validator import ScheduleValidator, ValidationResult
from .statistics import ScheduleStatistics


class Course:
    def __init__(self, course_id: str, name: str, teacher_id: str, class_id: str,
                 required_hours: int, student_count: int = 30, room_type: str = "normal",
                 fixed_room_id: str = None, priority: int = 0):
        self.course_id = course_id
        self.name = name
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.required_hours = required_hours
        self.student_count = student_count
        self.room_type = room_type
        self.fixed_room_id = fixed_room_id
        self.priority = priority

    def to_dict(self) -> Dict:
        return {
            "course_id": self.course_id,
            "name": self.name,
            "teacher_id": self.teacher_id,
            "class_id": self.class_id,
            "required_hours": self.required_hours,
            "student_count": self.student_count,
            "room_type": self.room_type,
            "fixed_room_id": self.fixed_room_id,
            "priority": self.priority,
        }

    def __repr__(self):
        return f"Course({self.course_id}, {self.name}, hours={self.required_hours})"


class MainScheduler:
    def __init__(self, start_date: str = None):
        self.time_pool = TimePool(start_date)
        self.holiday_manager = HolidayManager()
        self.room_allocator = RoomAllocator()
        self.constraint_checker = ConstraintChecker()
        self.optimizer = ScheduleOptimizer()
        self.validator = ScheduleValidator()
        self.statistics = ScheduleStatistics()

        self.schedule = {}
        self.failed_courses = []
        self.scheduling_log = []

    def setup_holidays(self, holidays: Dict[str, Dict]):
        self.holiday_manager.set_holidays(holidays)
        self.holiday_manager.mark_holidays_in_pool(self.time_pool)

    def add_room(self, room_id: str, name: str, capacity: int, room_type: str = "normal",
                 fixed: bool = False, building: str = ""):
        self.room_allocator.add_room(room_id, name, capacity, room_type, fixed, building)

    def schedule_courses(self, courses: List[Course]) -> Dict:
        self.schedule = {}
        self.failed_courses = []
        self.scheduling_log = []

        sorted_courses = self._sort_courses_by_priority(courses)

        for course in sorted_courses:
            success = self._schedule_single_course(course)

            if success:
                self.scheduling_log.append({
                    "course_id": course.course_id,
                    "status": "success",
                    "message": f"课程 {course.course_id} 排课成功"
                })
            else:
                self.failed_courses.append(course)
                self.scheduling_log.append({
                    "course_id": course.course_id,
                    "status": "failed",
                    "message": f"课程 {course.course_id} 排课失败"
                })

        return self.schedule

    def _schedule_single_course(self, course: Course) -> bool:
        required_hours = course.required_hours
        scheduled_hours = 0

        preferred_periods = ["morning", "afternoon", "evening"]

        for period in preferred_periods:
            if scheduled_hours >= required_hours:
                break

            period_hours = self.time_pool.get_period_hours(period)
            sessions_needed = (required_hours - scheduled_hours + period_hours - 1) // period_hours

            for _ in range(sessions_needed):
                if scheduled_hours >= required_hours:
                    break

                best_slot = self._find_best_slot_for_period(course, period)

                if best_slot:
                    week, day, period_name, room_id = best_slot
                    self._assign_course_to_slot(course, week, day, period_name, room_id)
                    scheduled_hours += self.time_pool.get_period_hours(period_name)
                else:
                    if period == "evening":
                        return scheduled_hours > 0
                    continue

        return scheduled_hours >= required_hours

    def _find_best_slot_for_period(self, course: Course, target_period: str) -> Optional[Tuple]:
        candidate_slots = []

        for week in range(1, 17):
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                if self.time_pool.is_available(week, day, target_period):
                    rooms = self.room_allocator.find_available_rooms(
                        required_capacity=course.student_count,
                        required_type=course.room_type,
                        week=week,
                        day=day,
                        period=target_period,
                        fixed_room_id=course.fixed_room_id
                    )

                    for room in rooms:
                        candidate_slots.append((week, day, target_period, room.room_id))

        if not candidate_slots:
            return None

        best_slot = self.optimizer.find_best_slot(
            course,
            candidate_slots,
            self.time_pool,
            self.room_allocator,
            self.schedule,
            self.constraint_checker,
            self.holiday_manager
        )

        return best_slot

    def _assign_course_to_slot(self, course: Course, week: int, day: str, period: str,
                               room_id: str):
        slot_key = f"W{week}_D{day}_{period}"

        if slot_key not in self.schedule:
            self.schedule[slot_key] = []

        self.schedule[slot_key].append({
            "course_id": course.course_id,
            "teacher_id": course.teacher_id,
            "class_id": course.class_id,
            "room_id": room_id,
            "week": week,
            "day": day,
            "period": period,
            "course_name": course.name,
        })

        self.room_allocator.allocate_room(room_id, week, day, period)
        self.time_pool.remove_slot(week, day, period)

    def _sort_courses_by_priority(self, courses: List[Course]) -> List[Course]:
        return sorted(courses, key=lambda c: (c.priority, c.required_hours), reverse=True)

    def validate_schedule(self) -> ValidationResult:
        courses = self._get_all_courses()
        return self.validator.validate_schedule(
            self.schedule, courses, self.time_pool,
            self.room_allocator, self.holiday_manager
        )

    def get_statistics(self) -> Dict:
        courses = self._get_all_courses()
        return self.statistics.generate_full_report(self.schedule, courses)

    def get_failed_courses(self) -> List[Course]:
        return self.failed_courses

    def get_scheduling_log(self) -> List[Dict]:
        return self.scheduling_log

    def reset(self):
        self.schedule = {}
        self.failed_courses = []
        self.scheduling_log = []
        self.time_pool.reset()
        self.room_allocator.clear_schedule()

    def _get_all_courses(self) -> List[Course]:
        course_map = {}

        for slot_key, sessions in self.schedule.items():
            for session in sessions:
                course_id = session.get('course_id')
                if course_id and course_id not in course_map:
                    course_map[course_id] = Course(
                        course_id=course_id,
                        name=session.get('course_name', ''),
                        teacher_id=session.get('teacher_id', ''),
                        class_id=session.get('class_id', ''),
                        required_hours=0,
                    )

        for course in self.failed_courses:
            if course.course_id not in course_map:
                course_map[course.course_id] = course

        return list(course_map.values())
