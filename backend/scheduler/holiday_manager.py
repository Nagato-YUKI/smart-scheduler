from typing import Dict, List, Set
from datetime import date, datetime


class HolidayManager:
    def __init__(self):
        self.holidays = {}

    def add_holiday(self, date_obj: date, name: str = ""):
        date_str = date_obj.strftime("%Y-%m-%d")
        self.holidays[date_str] = {"date": date_obj, "name": name}

    def add_holidays(self, holidays_dict: Dict):
        for date_str, info in holidays_dict.items():
            if isinstance(info, dict) and "date" in info:
                self.holidays[date_str] = info
            else:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    self.holidays[date_str] = {"date": date_obj, "name": info.get("name", "")}
                except ValueError:
                    pass

    def is_holiday(self, date_obj: date) -> bool:
        date_str = date_obj.strftime("%Y-%m-%d")
        return date_str in self.holidays

    def get_holiday_name(self, date_obj: date) -> str:
        date_str = date_obj.strftime("%Y-%m-%d")
        if date_str in self.holidays:
            return self.holidays[date_str].get("name", "节假日")
        return ""

    def get_all_holidays(self) -> Dict:
        return self.holidays.copy()

    def get_holidays_in_range(self, start_date: date, end_date: date) -> List[Dict]:
        result = []
        for date_str, info in self.holidays.items():
            holiday_date = info["date"]
            if start_date <= holiday_date <= end_date:
                result.append({"date": holiday_date, "name": info.get("name", ""), "date_str": date_str})
        return sorted(result, key=lambda x: x["date"])

    def remove_holiday(self, date_obj: date) -> bool:
        date_str = date_obj.strftime("%Y-%m-%d")
        if date_str in self.holidays:
            del self.holidays[date_str]
            return True
        return False

    def clear_holidays(self):
        self.holidays.clear()
