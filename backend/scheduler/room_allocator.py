from typing import List, Dict, Optional, Tuple


class Room:
    def __init__(self, room_id: str, name: str, capacity: int, room_type: str = "normal",
                 fixed: bool = False, building: str = ""):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type
        self.fixed = fixed
        self.building = building

    def to_dict(self) -> Dict:
        return {
            "room_id": self.room_id,
            "name": self.name,
            "capacity": self.capacity,
            "room_type": self.room_type,
            "fixed": self.fixed,
            "building": self.building,
        }

    def __repr__(self):
        return f"Room({self.room_id}, {self.name}, cap={self.capacity}, type={self.room_type})"


class RoomAllocator:
    ROOM_TYPES = ["normal", "lab", "computer", "music", "art", "sports", "lecture"]

    def __init__(self):
        self.rooms = {}
        self.room_schedule = {}

    def add_room(self, room_id: str, name: str, capacity: int, room_type: str = "normal",
                 fixed: bool = False, building: str = ""):
        room = Room(room_id, name, capacity, room_type, fixed, building)
        self.rooms[room_id] = room
        self.room_schedule[room_id] = set()

    def remove_room(self, room_id: str):
        if room_id in self.rooms:
            del self.rooms[room_id]
        if room_id in self.room_schedule:
            del self.room_schedule[room_id]

    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def get_all_rooms(self) -> List[Room]:
        return list(self.rooms.values())

    def get_rooms_by_type(self, room_type: str) -> List[Room]:
        return [r for r in self.rooms.values() if r.room_type == room_type]

    def get_rooms_by_capacity(self, min_capacity: int) -> List[Room]:
        return [r for r in self.rooms.values() if r.capacity >= min_capacity]

    def is_room_available(self, room_id: str, week: int, day: str, period: str) -> bool:
        if room_id not in self.room_schedule:
            return False

        slot_key = f"W{week}_D{day}_{period}"
        return slot_key not in self.room_schedule[room_id]

    def allocate_room(self, room_id: str, week: int, day: str, period: str) -> bool:
        if room_id not in self.rooms:
            return False

        if not self.is_room_available(room_id, week, day, period):
            return False

        slot_key = f"W{week}_D{day}_{period}"
        self.room_schedule[room_id].add(slot_key)
        return True

    def deallocate_room(self, room_id: str, week: int, day: str, period: str):
        if room_id in self.room_schedule:
            slot_key = f"W{week}_D{day}_{period}"
            self.room_schedule[room_id].discard(slot_key)

    def find_best_room(self, required_capacity: int, required_type: str = "normal",
                       fixed_room_id: str = None) -> Optional[Room]:
        if fixed_room_id:
            room = self.rooms.get(fixed_room_id)
            if room and room.capacity >= required_capacity:
                return room
            return None

        candidates = [
            r for r in self.rooms.values()
            if r.room_type == required_type and r.capacity >= required_capacity
        ]

        if not candidates:
            candidates = [
                r for r in self.rooms.values()
                if r.capacity >= required_capacity
            ]

        if not candidates:
            return None

        return min(candidates, key=lambda r: r.capacity)

    def find_available_rooms(self, required_capacity: int, required_type: str = "normal",
                             week: int = None, day: str = None, period: str = None,
                             fixed_room_id: str = None) -> List[Room]:
        if fixed_room_id:
            room = self.rooms.get(fixed_room_id)
            if room and room.capacity >= required_capacity:
                if week is None or self.is_room_available(room.room_id, week, day, period):
                    return [room]
            return []

        candidates = [
            r for r in self.rooms.values()
            if r.room_type == required_type and r.capacity >= required_capacity
        ]

        if not candidates:
            candidates = [
                r for r in self.rooms.values()
                if r.capacity >= required_capacity
            ]

        if week is not None and day is not None and period is not None:
            candidates = [
                r for r in candidates
                if self.is_room_available(r.room_id, week, day, period)
            ]

        candidates.sort(key=lambda r: r.capacity)
        return candidates

    def get_room_usage_stats(self) -> Dict[str, Dict]:
        stats = {}
        for room_id, room in self.rooms.items():
            total_slots = len(self.room_schedule.get(room_id, set()))
            stats[room_id] = {
                "name": room.name,
                "capacity": room.capacity,
                "room_type": room.room_type,
                "used_slots": total_slots,
            }
        return stats

    def clear_schedule(self):
        for room_id in self.room_schedule:
            self.room_schedule[room_id] = set()
