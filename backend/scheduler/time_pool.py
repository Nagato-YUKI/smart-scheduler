from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime, timedelta, date
from collections import defaultdict
import logging


class TimePool:
    def __init__(self):
        self.time_slots = set()
        self.available_slots = set()
        self.week_dates = {}
        self.teacher_daily_sessions = defaultdict(lambda: defaultdict(int))
        self.class_daily_sessions = defaultdict(lambda: defaultdict(int))
        self.max_teacher_daily_sessions = 2
        self.max_class_daily_sessions = 8
        self.teacher_weekly_sessions = defaultdict(lambda: defaultdict(int))
        self.max_teacher_weekly_sessions = 5
        self.logger = logging.getLogger(__name__)

    def generate_time_slots(self, start_date: datetime, total_weeks: int = 16,
                            school_days: List[str] = None, periods: Dict = None):
        school_days = school_days or ["monday", "tuesday", "wednesday", "thursday", "friday"]
        periods = periods or {
            "morning": ["8:00-8:45", "8:55-9:40", "10:00-10:45", "10:55-11:40"],
            "afternoon": ["14:00-14:45", "14:55-15:40", "16:00-16:45", "16:55-17:40"],
            "evening": ["18:30-19:15", "19:25-20:10", "20:20-21:05"],
        }
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }
        for week in range(1, total_weeks + 1):
            for day in school_days:
                day_offset = day_map[day]
                week_start = start_date + timedelta(weeks=week - 1)
                current_date = week_start + timedelta(days=day_offset)
                self.week_dates[(week, day)] = current_date
                for period in periods:
                    self.time_slots.add((week, day, period))
                    self.available_slots.add((week, day, period))

    def update_holidays(self, holiday_manager):
        for week, day in list(self.available_slots):
            date = self.get_date(week, day)
            if date and holiday_manager.is_holiday(date):
                for period in ["morning", "afternoon", "evening"]:
                    self.available_slots.discard((week, day, period))

    def get_date(self, week: int, day: str) -> Optional[date]:
        return self.week_dates.get((week, day))

    def is_available(self, week: int, day: str, period: str) -> bool:
        return (week, day, period) in self.available_slots

    def remove_slot(self, week: int, day: str, period: str):
        self.available_slots.discard((week, day, period))

    def add_slot(self, week: int, day: str, period: str):
        if (week, day, period) in self.time_slots:
            self.available_slots.add((week, day, period))

    def get_available_slots(self) -> Set[Tuple]:
        return self.available_slots.copy()

    def initialize_teacher_constraints(self):
        pass

    def check_teacher_capacity(self, teacher_id: str, week: int, day: str) -> bool:
        daily_count = self.teacher_daily_sessions[teacher_id].get(f"W{week}_D{day}", 0)
        return daily_count < self.max_teacher_daily_sessions

    def record_teacher_session(self, teacher_id: str, week: int, day: str):
        self.teacher_daily_sessions[teacher_id][f"W{week}_D{day}"] += 1
        self.teacher_weekly_sessions[teacher_id][week] += 1

    def check_class_capacity(self, class_id: str, week: int, day: str) -> bool:
        daily_count = self.class_daily_sessions[class_id].get(f"W{week}_D{day}", 0)
        return daily_count < self.max_class_daily_sessions

    def record_class_session(self, class_id: str, week: int, day: str):
        self.class_daily_sessions[class_id][f"W{week}_D{day}"] += 1

    def get_teacher_weekly_sessions(self, teacher_id: str, week: int) -> int:
        return self.teacher_weekly_sessions[teacher_id].get(week, 0)
