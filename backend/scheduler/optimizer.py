from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class ScheduleOptimizer:
    def __init__(self):
        self.optimizer_weights = {
            "teacher_concentration": 0.3,
            "class_balance": 0.3,
            "capacity_match": 0.2,
            "period_preference": 0.2,
        }

    def calculate_teacher_concentration_score(self, teacher_id: str, schedule: Dict,
                                              week: int, day: str) -> float:
        teacher_days = defaultdict(set)

        for key, sessions in schedule.items():
            for session in sessions:
                if session.get('teacher_id') == teacher_id:
                    w = session.get('week')
                    d = session.get('day')
                    if w is not None and d is not None:
                        teacher_days[w].add(d)

        current_week_days = teacher_days.get(week, set())
        new_day_count = len(current_week_days | {day})

        if len(current_week_days) == 0:
            return 1.0

        if day in current_week_days:
            return 1.0

        return max(0, 1.0 - (new_day_count - len(current_week_days)) * 0.3)

    def calculate_class_balance_score(self, class_id: str, schedule: Dict,
                                      week: int, day: str) -> float:
        class_days = defaultdict(set)

        for key, sessions in schedule.items():
            for session in sessions:
                if session.get('class_id') == class_id:
                    w = session.get('week')
                    d = session.get('day')
                    if w is not None and d is not None:
                        class_days[w].add(d)

        current_week_days = class_days.get(week, set())

        if len(current_week_days) == 0:
            return 1.0

        if day in current_week_days:
            day_courses = sum(
                1 for s in schedule.get(f"W{week}_D{day}_morning", [])
                if s.get('class_id') == class_id
            )
            day_courses += sum(
                1 for s in schedule.get(f"W{week}_D{day}_afternoon", [])
                if s.get('class_id') == class_id
            )
            day_courses += sum(
                1 for s in schedule.get(f"W{week}_D{day}_evening", [])
                if s.get('class_id') == class_id
            )

            if day_courses >= 3:
                return 0.3
            return 0.7

        return 1.0

    def calculate_capacity_match_score(self, course, room) -> float:
        required = getattr(course, 'student_count', 0)
        capacity = room.capacity

        if capacity < required:
            return 0.0

        ratio = required / capacity if capacity > 0 else 0

        if 0.7 <= ratio <= 1.0:
            return 1.0
        elif 0.5 <= ratio < 0.7:
            return 0.7
        elif ratio < 0.5:
            return 0.4

        return 0.5

    def calculate_period_preference_score(self, period: str) -> float:
        if period == "morning":
            return 1.0
        elif period == "afternoon":
            return 0.8
        else:
            return 0.5

    def calculate_slot_score(self, course, room_id: str, room, week: int, day: str,
                             period: str, schedule: Dict, room_allocator) -> float:
        teacher_id = getattr(course, 'teacher_id', None)
        class_id = getattr(course, 'class_id', None)

        if teacher_id:
            teacher_score = self.calculate_teacher_concentration_score(
                teacher_id, schedule, week, day
            )
        else:
            teacher_score = 1.0

        if class_id:
            class_score = self.calculate_class_balance_score(
                class_id, schedule, week, day
            )
        else:
            class_score = 1.0

        capacity_score = self.calculate_capacity_match_score(course, room)

        period_score = self.calculate_period_preference_score(period)

        weights = self.optimizer_weights
        total_score = (
                teacher_score * weights["teacher_concentration"] +
                class_score * weights["class_balance"] +
                capacity_score * weights["capacity_match"] +
                period_score * weights["period_preference"]
        )

        return total_score

    def find_best_slot(self, course, candidate_slots: List[Tuple], time_pool,
                       room_allocator, schedule, constraint_checker, holiday_manager) -> Optional[
        Tuple]:
        best_slot = None
        best_score = -1

        for week, day, period, room_id in candidate_slots:
            room = room_allocator.get_room(room_id)
            if room is None:
                continue

            is_valid, violations = constraint_checker.check_all_hard_constraints(
                course, room_id, week, day, period, schedule,
                time_pool, room_allocator, holiday_manager
            )

            if not is_valid:
                continue

            score = self.calculate_slot_score(
                course, room_id, room, week, day, period, schedule, room_allocator
            )

            if score > best_score:
                best_score = score
                best_slot = (week, day, period, room_id)

        return best_slot

    def optimize_schedule(self, schedule: Dict, courses: List, time_pool,
                          room_allocator, constraint_checker, holiday_manager) -> Dict:
        sorted_courses = sorted(
            courses,
            key=lambda c: getattr(c, 'priority', 0),
            reverse=True
        )

        for course in sorted_courses:
            best_slot = self.find_best_slot(
                course,
                self._generate_candidate_slots(time_pool, course),
                time_pool,
                room_allocator,
                schedule,
                constraint_checker,
                holiday_manager
            )

            if best_slot:
                week, day, period, room_id = best_slot
                slot_key = f"W{week}_D{day}_{period}"

                if slot_key not in schedule:
                    schedule[slot_key] = []

                schedule[slot_key].append({
                    "course_id": getattr(course, 'course_id', ''),
                    "teacher_id": getattr(course, 'teacher_id', ''),
                    "class_id": getattr(course, 'class_id', ''),
                    "room_id": room_id,
                    "week": week,
                    "day": day,
                    "period": period,
                })

                room_allocator.allocate_room(room_id, week, day, period)
                time_pool.remove_slot(week, day, period)

        return schedule

    def _generate_candidate_slots(self, time_pool, course) -> List[Tuple]:
        candidates = []
        preferred_order = ["morning", "afternoon", "evening"]

        for week in range(1, 17):
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                for period in preferred_order:
                    if time_pool.is_available(week, day, period):
                        candidates.append((week, day, period, None))

        return candidates

    def set_weights(self, teacher_concentration: float = None, class_balance: float = None,
                    capacity_match: float = None, period_preference: float = None):
        if teacher_concentration is not None:
            self.optimizer_weights["teacher_concentration"] = teacher_concentration
        if class_balance is not None:
            self.optimizer_weights["class_balance"] = class_balance
        if capacity_match is not None:
            self.optimizer_weights["capacity_match"] = capacity_match
        if period_preference is not None:
            self.optimizer_weights["period_preference"] = period_preference
