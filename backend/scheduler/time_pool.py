from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class TimeSlot:
    def __init__(self, week: int, day: int, period: str):
        self.week = week
        self.day = day
        self.period = period

    def to_key(self) -> str:
        return f"W{self.week}_D{self.day}_{self.period}"

    def __repr__(self):
        return f"TimeSlot(week={self.week}, day={self.day}, period={self.period})"

    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return False
        return self.week == other.week and self.day == other.day and self.period == other.period

    def __hash__(self):
        return hash(self.to_key())


class TimePool:
    WEEKS = 16
    DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    PERIODS = ["morning", "afternoon", "evening"]

    PERIOD_HOURS = {
        "morning": 4,
        "afternoon": 4,
        "evening": 3,
    }

    def __init__(self, start_date: str = None):
        if start_date:
            self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            self.start_date = datetime.now()

        self.time_slots = []
        self.available_slots = set()
        self.week_start_dates = {}
        self._generate_time_slots()

    def _generate_time_slots(self):
        self.time_slots = []
        self.available_slots = set()

        for week in range(1, self.WEEKS + 1):
            week_start = self.start_date + timedelta(weeks=week - 1)
            self.week_start_dates[week] = week_start

            for day_idx, day_name in enumerate(self.DAYS):
                day_date = week_start + timedelta(days=day_idx)

                for period in self.PERIODS:
                    slot = TimeSlot(week, day_name, period)
                    self.time_slots.append(slot)
                    self.available_slots.add(slot.to_key())

    def get_date(self, week: int, day_name: str) -> datetime:
        if week not in self.week_start_dates:
            return None

        day_idx = self.DAYS.index(day_name)
        return self.week_start_dates[week] + timedelta(days=day_idx)

    def get_period_hours(self, period: str) -> int:
        return self.PERIOD_HOURS.get(period, 0)

    def get_week_day_date(self, week: int, day: str) -> datetime:
        if week not in self.week_start_dates:
            return None
        day_idx = self.DAYS.index(day)
        return self.week_start_dates[week] + timedelta(days=day_idx)

    def remove_slot(self, week: int, day: str, period: str):
        key = f"W{week}_D{day}_{period}"
        self.available_slots.discard(key)

    def add_slot(self, week: int, day: str, period: str):
        key = f"W{week}_D{day}_{period}"
        self.available_slots.add(key)

    def is_available(self, week: int, day: str, period: str) -> bool:
        key = f"W{week}_D{day}_{period}"
        return key in self.available_slots

    def get_available_slots(self) -> List[TimeSlot]:
        slots = []
        for slot in self.time_slots:
            if slot.to_key() in self.available_slots:
                slots.append(slot)
        return slots

    def get_slots_by_week(self, week: int) -> List[TimeSlot]:
        return [s for s in self.time_slots if s.week == week]

    def get_slots_by_day(self, week: int, day: str) -> List[TimeSlot]:
        return [s for s in self.time_slots if s.week == week and s.day == day]

    def get_total_available_hours(self) -> int:
        total = 0
        for key in self.available_slots:
            parts = key.split("_")
            period = parts[2]
            total += self.get_period_hours(period)
        return total

    def reset(self):
        self._generate_time_slots()
