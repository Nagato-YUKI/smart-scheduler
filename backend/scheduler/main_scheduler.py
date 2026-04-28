import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
import logging
from collections import defaultdict

from .time_pool import TimePool
from .room_allocator import RoomAllocator
from .holiday_manager import HolidayManager
from .constraints import ConstraintChecker
from .optimizer import ScheduleOptimizer
from .validator import ScheduleValidator
from .statistics import ScheduleStatistics


class SchedulerCourse:
    def __init__(self, course_id: str, name: str, teacher_id: str,
                 class_id: str, required_hours: int = 64, student_count: int = 30,
                 room_type: str = 'normal', priority: int = 0,
                 preferred_days: List[str] = None, preferred_periods: List[str] = None,
                 fixed_room_id: str = None, is_continuous: bool = False,
                 max_continuous_sessions: int = 2):
        self.course_id = course_id
        self.name = name
        self.teacher_id = teacher_id
        self.class_id = class_id
        self.required_hours = required_hours
        self.student_count = student_count
        self.room_type = room_type
        self.priority = priority
        self.preferred_days = preferred_days or ["monday", "tuesday", "wednesday", "thursday", "friday"]
        self.preferred_periods = preferred_periods or ["morning", "afternoon", "evening"]
        self.fixed_room_id = fixed_room_id
        self.is_continuous = is_continuous
        self.max_continuous_sessions = max_continuous_sessions


class AdvancedScheduler:
    def __init__(self):
        self.time_pool = TimePool()
        self.room_allocator = RoomAllocator()
        self.holiday_manager = HolidayManager()
        self.constraint_checker = ConstraintChecker()
        self.optimizer = ScheduleOptimizer()
        self.validator = ScheduleValidator()
        self.statistics = ScheduleStatistics()
        self.schedule = {}
        self.courses = []
        self.logger = logging.getLogger(__name__)

    def add_course(self, course: SchedulerCourse):
        self.courses.append(course)

    def add_room(self, room_id: str, name: str, capacity: int, room_type: str = 'normal'):
        self.room_allocator.add_room(room_id, name, capacity, room_type)

    def setup_holidays(self, holidays: Dict):
        self.holiday_manager.add_holidays(holidays)
        self.time_pool.update_holidays(self.holiday_manager)

    def configure_schedule(self, start_date: datetime, total_weeks: int = 16,
                           school_days: List[str] = None, periods: Dict = None):
        self.time_pool = TimePool()
        self.time_pool.generate_time_slots(start_date, total_weeks, school_days, periods)
        self.time_pool.update_holidays(self.holiday_manager)
        self.time_pool.initialize_teacher_constraints()

    def schedule_courses(self, courses: List[SchedulerCourse]) -> Dict:
        if not courses:
            return self.schedule

        self.courses = courses
        self.schedule = {}
        sorted_courses = sorted(self.courses, key=lambda c: getattr(c, 'priority', 0), reverse=True)

        for course in sorted_courses:
            try:
                required_sessions = getattr(course, 'required_hours', 64)
                scheduled_count = 0
                candidate_slots = self._get_candidate_slots(course)

                for slot_info in candidate_slots:
                    if scheduled_count >= required_sessions:
                        break
                    success = self._schedule_single_course(course, slot_info)
                    if success:
                        scheduled_count += 1

                if scheduled_count < required_sessions:
                    self.logger.warning(f"Course {course.course_id} scheduled {scheduled_count}/{required_sessions} sessions")

            except Exception as e:
                self.logger.error(f"Failed to schedule course {course.course_id}: {str(e)}")

        return self.schedule

    def _schedule_single_course(self, course: SchedulerCourse, slot_info: Tuple) -> bool:
        week, day, period, room_id = slot_info
        room = self.room_allocator.get_room(room_id)
        if room is None:
            return False

        is_valid, violations = self.constraint_checker.check_all_hard_constraints(
            course, room_id, week, day, period, self.schedule,
            self.time_pool, self.room_allocator, self.holiday_manager
        )

        if not is_valid:
            return False

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
        })

        self.room_allocator.allocate_room(room_id, week, day, period)
        self.time_pool.remove_slot(week, day, period)

        return True

    def _get_candidate_slots(self, course: SchedulerCourse) -> List[Tuple]:
        candidates = []
        for week in range(1, 17):
            for day in course.preferred_days:
                for period in course.preferred_periods:
                    if self.time_pool.is_available(week, day, period):
                        room_id = self.room_allocator.find_best_room(
                            course.room_type, course.student_count
                        )
                        if room_id:
                            candidates.append((week, day, period, room_id))
        return candidates

    def optimize_schedule(self) -> Dict:
        return self.optimizer.optimize_schedule(
            self.schedule, self.courses, self.time_pool,
            self.room_allocator, self.constraint_checker, self.holiday_manager
        )

    def validate_schedule(self) -> Dict:
        result = self.validator.validate_schedule(
            self.schedule, self.courses, self.time_pool,
            self.room_allocator, self.holiday_manager
        )
        return result.to_dict()

    def get_statistics(self) -> Dict:
        return self.statistics.generate_full_report(self.schedule, self.courses)

    def get_teacher_schedule(self, teacher_id: str) -> Dict:
        return self.statistics.get_teacher_schedule_summary(self.schedule, teacher_id)

    def get_class_schedule(self, class_id: str) -> Dict:
        return self.statistics.get_class_schedule_summary(self.schedule, class_id)

    def get_schedule_results(self) -> List[Dict]:
        results = []
        for slot_key, sessions in self.schedule.items():
            for session in sessions:
                results.append({
                    "teaching_class_id": session['course_id'],
                    "week": session['week'],
                    "day": session['day'],
                    "period": session['period'],
                    "room_id": session['room_id'],
                    "teacher_id": session['teacher_id'],
                    "class_id": session['class_id'],
                })
        return results
