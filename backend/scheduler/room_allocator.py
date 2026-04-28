from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class Room:
    def __init__(self, room_id: str, name: str, capacity: int, room_type: str = 'normal'):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type
        self.allocated_slots = set()

    def is_available(self, week: int, day: str, period: str) -> bool:
        return (week, day, period) not in self.allocated_slots

    def allocate(self, week: int, day: str, period: str):
        self.allocated_slots.add((week, day, period))

    def release(self, week: int, day: str, period: str):
        self.allocated_slots.discard((week, day, period))

    def __repr__(self):
        return f"Room({self.room_id}, {self.name}, {self.capacity}, {self.room_type})"


class RoomAllocator:
    def __init__(self):
        self.rooms = {}
        self.room_usage_count = defaultdict(int)

    def add_room(self, room_id: str, name: str, capacity: int, room_type: str = 'normal'):
        room = Room(room_id, name, capacity, room_type)
        self.rooms[room_id] = room

    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def find_best_room(self, required_type: str, student_count: int, excluded_room_ids: List[str] = None) -> Optional[str]:
        excluded_room_ids = excluded_room_ids or []
        suitable_rooms = []
        for room_id, room in self.rooms.items():
            if room_id in excluded_room_ids:
                continue
            if room.room_type == required_type and room.capacity >= student_count:
                suitable_rooms.append(room)
        if not suitable_rooms:
            for room_id, room in self.rooms.items():
                if room_id in excluded_room_ids:
                    continue
                if room.room_type == 'normal' and room.capacity >= student_count:
                    suitable_rooms.append(room)
        if not suitable_rooms:
            return None
        suitable_rooms.sort(key=lambda r: (r.capacity, self.room_usage_count[r.room_id]))
        best_room = suitable_rooms[0]
        return best_room.room_id

    def is_room_available(self, room_id: str, week: int, day: str, period: str) -> bool:
        room = self.rooms.get(room_id)
        if room:
            return room.is_available(week, day, period)
        return False

    def allocate_room(self, room_id: str, week: int, day: str, period: str) -> bool:
        room = self.rooms.get(room_id)
        if room and room.is_available(week, day, period):
            room.allocate(week, day, period)
            self.room_usage_count[room_id] += 1
            return True
        return False

    def release_room(self, room_id: str, week: int, day: str, period: str) -> bool:
        room = self.rooms.get(room_id)
        if room:
            room.release(week, day, period)
            self.room_usage_count[room_id] = max(0, self.room_usage_count[room_id] - 1)
            return True
        return False

    def get_room_schedule(self, room_id: str) -> List[Tuple]:
        room = self.rooms.get(room_id)
        if room:
            return list(room.allocated_slots)
        return []

    def get_all_room_types(self) -> Dict[str, int]:
        room_types = defaultdict(int)
        for room in self.rooms.values():
            room_types[room.room_type] += 1
        return dict(room_types)

    def get_room_usage_statistics(self) -> Dict[str, int]:
        return dict(self.room_usage_count)
