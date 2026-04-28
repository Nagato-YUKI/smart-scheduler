from typing import Dict, List, Optional
from collections import defaultdict


class ScheduleStatistics:
    PERIOD_HOURS = {"morning": 4, "afternoon": 4, "evening": 3}

    def __init__(self):
        self.stats_cache = {}

    def calculate_total_scheduled_hours(self, schedule: Dict) -> int:
        total_hours = 0
        for slot_key, sessions in schedule.items():
            parts = slot_key.split("_")
            if len(parts) >= 3:
                period = parts[2]
                hours = self.PERIOD_HOURS.get(period, 0)
                total_hours += hours * len(sessions)
        return total_hours

    def calculate_teacher_hours(self, schedule: Dict) -> Dict[str, int]:
        teacher_hours = defaultdict(int)
        for slot_key, sessions in schedule.items():
            parts = slot_key.split("_")
            if len(parts) >= 3:
                period = parts[2]
                hours = self.PERIOD_HOURS.get(period, 0)
                for session in sessions:
                    teacher_id = session.get('teacher_id')
                    if teacher_id:
                        teacher_hours[teacher_id] += hours
        return dict(teacher_hours)

    def calculate_class_hours(self, schedule: Dict) -> Dict[str, int]:
        class_hours = defaultdict(int)
        for slot_key, sessions in schedule.items():
            parts = slot_key.split("_")
            if len(parts) >= 3:
                period = parts[2]
                hours = self.PERIOD_HOURS.get(period, 0)
                for session in sessions:
                    class_id = session.get('class_id')
                    if class_id:
                        class_hours[class_id] += hours
        return dict(class_hours)

    def calculate_room_usage(self, schedule: Dict) -> Dict[str, int]:
        room_usage = defaultdict(int)
        for slot_key, sessions in schedule.items():
            for session in sessions:
                room_id = session.get('room_id')
                if room_id:
                    room_usage[room_id] += 1
        return dict(room_usage)

    def calculate_weekly_distribution(self, schedule: Dict) -> Dict[int, int]:
        weekly_hours = defaultdict(int)
        for slot_key, sessions in schedule.items():
            parts = slot_key.split("_")
            if len(parts) >= 3:
                week = int(parts[0][1:])
                period = parts[2]
                hours = self.PERIOD_HOURS.get(period, 0)
                weekly_hours[week] += hours * len(sessions)
        return dict(weekly_hours)

    def calculate_daily_distribution(self, schedule: Dict) -> Dict[str, int]:
        daily_hours = defaultdict(int)
        for slot_key, sessions in schedule.items():
            parts = slot_key.split("_")
            if len(parts) >= 3:
                day = parts[1][1:]
                period = parts[2]
                hours = self.PERIOD_HOURS.get(period, 0)
                daily_hours[day] += hours * len(sessions)
        return dict(daily_hours)

    def calculate_period_distribution(self, schedule: Dict) -> Dict[str, int]:
        period_hours = defaultdict(int)
        for slot_key, sessions in schedule.items():
            parts = slot_key.split("_")
            if len(parts) >= 3:
                period = parts[2]
                hours = self.PERIOD_HOURS.get(period, 0)
                period_hours[period] += hours * len(sessions)
        return dict(period_hours)

    def count_missing_courses(self, schedule: Dict, courses: List) -> List[str]:
        scheduled_ids = set()
        for slot_key, sessions in schedule.items():
            for session in sessions:
                course_id = session.get('course_id')
                if course_id:
                    scheduled_ids.add(course_id)
        missing = []
        for course in courses:
            course_id = getattr(course, 'course_id', None)
            if course_id and course_id not in scheduled_ids:
                missing.append(course_id)
        return missing

    def calculate_completion_rate(self, schedule: Dict, courses: List) -> float:
        if not courses:
            return 0.0
        scheduled_ids = set()
        for slot_key, sessions in schedule.items():
            for session in sessions:
                course_id = session.get('course_id')
                if course_id:
                    scheduled_ids.add(course_id)
        scheduled_count = sum(1 for c in courses if getattr(c, 'course_id', None) in scheduled_ids)
        return (scheduled_count / len(courses)) * 100

    def generate_full_report(self, schedule: Dict, courses: List) -> Dict:
        return {
            "total_scheduled_hours": self.calculate_total_scheduled_hours(schedule),
            "teacher_hours": self.calculate_teacher_hours(schedule),
            "class_hours": self.calculate_class_hours(schedule),
            "room_usage": self.calculate_room_usage(schedule),
            "weekly_distribution": self.calculate_weekly_distribution(schedule),
            "daily_distribution": self.calculate_daily_distribution(schedule),
            "period_distribution": self.calculate_period_distribution(schedule),
            "missing_courses": self.count_missing_courses(schedule, courses),
            "completion_rate": self.calculate_completion_rate(schedule, courses),
            "total_courses": len(courses),
            "scheduled_courses": len(set(s.get('course_id') for sessions in schedule.values() for s in sessions if s.get('course_id'))),
        }

    def get_teacher_schedule_summary(self, schedule: Dict, teacher_id: str) -> Dict:
        sessions = []
        total_hours = 0
        for slot_key, session_list in schedule.items():
            for session in session_list:
                if session.get('teacher_id') == teacher_id:
                    parts = slot_key.split("_")
                    if len(parts) >= 3:
                        period = parts[2]
                        hours = self.PERIOD_HOURS.get(period, 0)
                        total_hours += hours
                        sessions.append({"slot": slot_key, "week": session.get('week'), "day": session.get('day'), "period": period, "course_id": session.get('course_id'), "class_id": session.get('class_id'), "room_id": session.get('room_id'), "hours": hours})
        return {"teacher_id": teacher_id, "total_hours": total_hours, "session_count": len(sessions), "sessions": sessions}

    def get_class_schedule_summary(self, schedule: Dict, class_id: str) -> Dict:
        sessions = []
        total_hours = 0
        for slot_key, session_list in schedule.items():
            for session in session_list:
                if session.get('class_id') == class_id:
                    parts = slot_key.split("_")
                    if len(parts) >= 3:
                        period = parts[2]
                        hours = self.PERIOD_HOURS.get(period, 0)
                        total_hours += hours
                        sessions.append({"slot": slot_key, "week": session.get('week'), "day": session.get('day'), "period": period, "course_id": session.get('course_id'), "teacher_id": session.get('teacher_id'), "room_id": session.get('room_id'), "hours": hours})
        return {"class_id": class_id, "total_hours": total_hours, "session_count": len(sessions), "sessions": sessions}

    def clear_cache(self):
        self.stats_cache = {}
