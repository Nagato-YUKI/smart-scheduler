from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple


class HolidayManager:
    def __init__(self):
        self.holidays = {}
        self.holiday_dates = set()

    def set_holidays(self, holidays: Dict[str, Dict]):
        self.holidays = holidays
        self.holiday_dates = set()

        for holiday_id, holiday_info in holidays.items():
            start_date = holiday_info.get("start_date")
            end_date = holiday_info.get("end_date")

            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else start

                current = start
                while current <= end:
                    self.holiday_dates.add(current.strftime("%Y-%m-%d"))
                    current += timedelta(days=1)

    def add_holiday(self, holiday_id: str, start_date: str, end_date: str = None, name: str = ""):
        if end_date is None:
            end_date = start_date

        self.holidays[holiday_id] = {
            "start_date": start_date,
            "end_date": end_date,
            "name": name,
        }

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        current = start
        while current <= end:
            self.holiday_dates.add(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

    def remove_holiday(self, holiday_id: str):
        if holiday_id in self.holidays:
            holiday_info = self.holidays[holiday_id]
            start = datetime.strptime(holiday_info["start_date"], "%Y-%m-%d")
            end = datetime.strptime(holiday_info["end_date"], "%Y-%m-%d")

            current = start
            while current <= end:
                date_str = current.strftime("%Y-%m-%d")
                self.holiday_dates.discard(date_str)
                current += timedelta(days=1)

            del self.holidays[holiday_id]

    def is_holiday(self, date: datetime) -> bool:
        return date.strftime("%Y-%m-%d") in self.holiday_dates

    def get_holiday_slots(self, time_pool) -> List[Tuple[int, str, str]]:
        holiday_slots = []

        for week in range(1, 17):
            for day_name in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                date = time_pool.get_date(week, day_name)
                if date and self.is_holiday(date):
                    for period in ["morning", "afternoon", "evening"]:
                        holiday_slots.append((week, day_name, period))

        return holiday_slots

    def mark_holidays_in_pool(self, time_pool):
        holiday_slots = self.get_holiday_slots(time_pool)
        for week, day, period in holiday_slots:
            time_pool.remove_slot(week, day, period)
        return len(holiday_slots)

    def get_holidays_in_week(self, week: int, time_pool) -> List[datetime]:
        holidays_in_week = []
        for day_name in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            date = time_pool.get_date(week, day_name)
            if date and self.is_holiday(date):
                holidays_in_week.append(date)
        return holidays_in_week

    def get_holiday_count(self, start_date: datetime = None, end_date: datetime = None) -> int:
        if start_date is None or end_date is None:
            return len(self.holiday_dates)

        count = 0
        current = start_date
        while current <= end_date:
            if current.strftime("%Y-%m-%d") in self.holiday_dates:
                count += 1
            current += timedelta(days=1)
        return count

    def clear(self):
        self.holidays = {}
        self.holiday_dates = set()
