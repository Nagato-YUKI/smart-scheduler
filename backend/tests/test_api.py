"""API接口集成测试"""
import pytest
import json
import time

from models import Room, Teacher, Class, Course, Holiday, TeachingClass, ScheduleEntry
from extensions import db


class TestHealthAPI:
    """测试健康检查接口"""

    def test_index(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'message' in data

    def test_health(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'


class TestRoomAPI:
    """测试教室CRUD API"""

    def test_get_rooms_empty(self, client):
        resp = client.get('/api/rooms')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['rooms'] == []

    def test_create_room(self, client):
        suffix = str(int(time.time() * 1000))
        resp = client.post('/api/rooms', json={
            'room_number': f'AR001_{suffix}',
            'name': '101教室',
            'capacity': 50,
            'room_type': '普通教室',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['room']['capacity'] == 50

    def test_create_room_duplicate_number(self, client):
        suffix = str(int(time.time() * 1000))
        client.post('/api/rooms', json={
            'room_number': f'AR002_{suffix}',
            'name': '201教室',
            'capacity': 40,
            'room_type': '普通教室',
        })
        resp = client.post('/api/rooms', json={
            'room_number': f'AR002_{suffix}',
            'name': '202教室',
            'capacity': 40,
            'room_type': '普通教室',
        })
        assert resp.status_code == 400

    def test_create_room_missing_fields(self, client):
        resp = client.post('/api/rooms', json={
            'room_number': 'AR003',
        })
        assert resp.status_code == 400

    def test_create_room_invalid_type(self, client):
        resp = client.post('/api/rooms', json={
            'room_number': 'AR004',
            'name': '测试教室',
            'capacity': 50,
            'room_type': '不存在的类型',
        })
        assert resp.status_code == 400

    def test_create_room_empty_body(self, client):
        resp = client.post('/api/rooms', data=b'', content_type='application/json')
        assert resp.status_code in (400, 415)

    def test_get_room(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR010_{suffix}', name='获取教室', capacity=50, room_type='普通教室')
        session.add(room)
        session.commit()
        room_id = room.id

        resp = client.get(f'/api/rooms/{room_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['room_number'] == f'AR010_{suffix}'

    def test_get_room_not_found(self, client):
        resp = client.get('/api/rooms/99999')
        assert resp.status_code == 404

    def test_update_room(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR011_{suffix}', name='更新教室', capacity=50, room_type='普通教室')
        session.add(room)
        session.commit()
        room_id = room.id

        resp = client.put(f'/api/rooms/{room_id}', json={
            'name': '新名称',
            'capacity': 60,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['room']['name'] == '新名称'
        assert data['room']['capacity'] == 60

    def test_update_room_not_found(self, client):
        resp = client.put('/api/rooms/99999', json={'name': '测试'})
        assert resp.status_code == 404

    def test_update_room_empty_body(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR012_{suffix}', name='更新教室', capacity=50, room_type='普通教室')
        session.add(room)
        session.commit()

        resp = client.put(f'/api/rooms/{room.id}', data=b'', content_type='application/json')
        assert resp.status_code in (400, 415)

    def test_update_room_duplicate_number(self, client, session):
        suffix = str(int(time.time() * 1000))
        room1 = Room(room_number=f'AR020_{suffix}', name='教室1', capacity=50, room_type='普通教室')
        room2 = Room(room_number=f'AR021_{suffix}', name='教室2', capacity=40, room_type='普通教室')
        session.add_all([room1, room2])
        session.commit()

        resp = client.put(f'/api/rooms/{room2.id}', json={
            'room_number': room1.room_number,
        })
        assert resp.status_code == 400

    def test_update_room_invalid_type(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR022_{suffix}', name='教室', capacity=50, room_type='普通教室')
        session.add(room)
        session.commit()

        resp = client.put(f'/api/rooms/{room.id}', json={
            'room_type': '无效类型'
        })
        assert resp.status_code == 400

    def test_delete_room(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR015_{suffix}', name='删除教室', capacity=50, room_type='普通教室')
        session.add(room)
        session.commit()
        room_id = room.id

        resp = client.delete(f'/api/rooms/{room_id}')
        assert resp.status_code == 200

        resp = client.get(f'/api/rooms/{room_id}')
        assert resp.status_code == 404

    def test_delete_room_with_references(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR016_{suffix}', name='引用教室', capacity=50, room_type='普通教室')
        session.add(room)
        session.flush()

        teaching_class = TeachingClass(
            course_id=99999,
            class_id=99999,
            teacher_id=99999,
            assigned_room_id=room.id,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(teaching_class)
        session.commit()
        room_id = room.id

        resp = client.delete(f'/api/rooms/{room_id}')
        assert resp.status_code == 400

    def test_get_rooms_with_filter(self, client, session):
        suffix = str(int(time.time() * 1000))
        room1 = Room(room_number=f'AR030_{suffix}', name='普通教室1', capacity=50, room_type='普通教室')
        room2 = Room(room_number=f'AR031_{suffix}', name='多媒体教室1', capacity=60, room_type='多媒体教室')
        session.add_all([room1, room2])
        session.commit()

        resp = client.get('/api/rooms?room_type=普通教室')
        assert resp.status_code == 200
        data = resp.get_json()
        assert all(r['room_type'] == '普通教室' for r in data['rooms'])

    def test_get_rooms_pagination(self, client, session):
        suffix = str(int(time.time() * 1000))
        for i in range(30):
            room = Room(
                room_number=f'AR1{i:02d}_{suffix}',
                name=f'分页教室{i}',
                capacity=50,
                room_type='普通教室'
            )
            session.add(room)
        session.commit()

        resp = client.get('/api/rooms?page=1&per_page=10')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['rooms']) <= 10
        assert data['current_page'] == 1


class TestTeacherAPI:
    """测试教师CRUD API"""

    def test_get_teachers_empty(self, client):
        resp = client.get('/api/teachers')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['teachers'] == []

    def test_create_teacher(self, client):
        suffix = str(int(time.time() * 1000))
        resp = client.post('/api/teachers', json={
            'teacher_number': f'AT001_{suffix}',
            'name': '张老师',
            'teachable_courses': ['数学', '物理'],
            'max_classes': 3,
            'max_weekly_sessions': 5,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['teacher']['name'] == '张老师'

    def test_create_teacher_duplicate_number(self, client):
        suffix = str(int(time.time() * 1000))
        client.post('/api/teachers', json={
            'teacher_number': f'AT002_{suffix}',
            'name': '李老师',
        })
        resp = client.post('/api/teachers', json={
            'teacher_number': f'AT002_{suffix}',
            'name': '王老师',
        })
        assert resp.status_code == 400

    def test_create_teacher_missing_fields(self, client):
        resp = client.post('/api/teachers', json={
            'teacher_number': 'AT003',
        })
        assert resp.status_code == 400

    def test_create_teacher_empty_body(self, client):
        resp = client.post('/api/teachers', data=b'', content_type='application/json')
        assert resp.status_code in (400, 415)

    def test_create_teacher_too_many_courses(self, client):
        suffix = str(int(time.time() * 1000))
        resp = client.post('/api/teachers', json={
            'teacher_number': f'AT004_{suffix}',
            'name': '赵老师',
            'teachable_courses': ['数学', '物理', '化学'],
        })
        assert resp.status_code == 400

    def test_get_teacher(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT010_{suffix}', name='获取教师')
        session.add(teacher)
        session.commit()
        teacher_id = teacher.id

        resp = client.get(f'/api/teachers/{teacher_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['name'] == '获取教师'

    def test_get_teacher_not_found(self, client):
        resp = client.get('/api/teachers/99999')
        assert resp.status_code == 404

    def test_update_teacher(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT011_{suffix}', name='更新教师')
        session.add(teacher)
        session.commit()
        teacher_id = teacher.id

        resp = client.put(f'/api/teachers/{teacher_id}', json={
            'name': '新名称',
            'max_classes': 4,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['teacher']['name'] == '新名称'

    def test_update_teacher_not_found(self, client):
        resp = client.put('/api/teachers/99999', json={'name': '测试'})
        assert resp.status_code == 404

    def test_update_teacher_empty_body(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT012_{suffix}', name='更新教师')
        session.add(teacher)
        session.commit()

        resp = client.put(f'/api/teachers/{teacher.id}', data=b'', content_type='application/json')
        assert resp.status_code in (400, 415)

    def test_update_teacher_duplicate_number(self, client, session):
        suffix = str(int(time.time() * 1000))
        t1 = Teacher(teacher_number=f'AT020_{suffix}', name='教师1')
        t2 = Teacher(teacher_number=f'AT021_{suffix}', name='教师2')
        session.add_all([t1, t2])
        session.commit()

        resp = client.put(f'/api/teachers/{t2.id}', json={
            'teacher_number': t1.teacher_number,
        })
        assert resp.status_code == 400

    def test_update_teacher_too_many_courses(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT022_{suffix}', name='教师')
        session.add(teacher)
        session.commit()

        resp = client.put(f'/api/teachers/{teacher.id}', json={
            'teachable_courses': ['数学', '物理', '化学'],
        })
        assert resp.status_code == 400

    def test_delete_teacher(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT015_{suffix}', name='删除教师')
        session.add(teacher)
        session.commit()
        teacher_id = teacher.id

        resp = client.delete(f'/api/teachers/{teacher_id}')
        assert resp.status_code == 200

        resp = client.get(f'/api/teachers/{teacher_id}')
        assert resp.status_code == 404

    def test_delete_teacher_with_courses(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT016_{suffix}', name='引用教师')
        session.add(teacher)
        session.flush()

        cls = Class(class_number=f'AC099_{suffix}', name='测试班级', student_count=30)
        session.add(cls)
        session.flush()

        course = Course(
            course_number=f'ACR099_{suffix}',
            name='测试课程',
            course_type='普通授课',
            teacher_id=teacher.id,
            class_id=cls.id,
        )
        session.add(course)
        session.commit()
        teacher_id = teacher.id

        resp = client.delete(f'/api/teachers/{teacher_id}')
        assert resp.status_code == 400

    def test_get_teachers_with_name_filter(self, client, session):
        suffix = str(int(time.time() * 1000))
        t1 = Teacher(teacher_number=f'AT030_{suffix}', name='张三')
        t2 = Teacher(teacher_number=f'AT031_{suffix}', name='李四')
        session.add_all([t1, t2])
        session.commit()

        resp = client.get('/api/teachers?name=张')
        assert resp.status_code == 200
        data = resp.get_json()
        assert all('张' in t['name'] for t in data['teachers'])

    def test_validate_teacher(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT040_{suffix}', name='验证教师')
        session.add(teacher)
        session.commit()

        resp = client.get(f'/api/teachers/{teacher.id}/validate')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'is_valid' in data

    def test_validate_teacher_not_found(self, client):
        resp = client.get('/api/teachers/99999/validate')
        assert resp.status_code == 404


class TestScheduleAPI:
    """测试排课API"""

    def test_run_schedule_empty(self, client, session):
        resp = client.post('/api/schedule/run', json={
            'start_date': '2026-03-02',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'message' in data

    def test_get_schedule_results_empty(self, client):
        resp = client.get('/api/schedule/results')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['results'] == []

    def test_run_schedule_with_data(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR100_{suffix}', name=f'排课教室_{suffix}', capacity=50, room_type='普通教室')
        session.add(room)

        teacher = Teacher(teacher_number=f'AT100_{suffix}', name=f'排课教师_{suffix}')
        session.add(teacher)

        cls = Class(class_number=f'AC100_{suffix}', name=f'排课班级_{suffix}', student_count=40)
        session.add(cls)
        session.flush()

        course = Course(
            course_number=f'ACR100_{suffix}',
            name=f'排课课程_{suffix}',
            course_type='普通授课',
            teacher_id=teacher.id,
            class_id=cls.id,
        )
        session.add(course)
        session.flush()

        teaching_class = TeachingClass(
            course_id=course.id,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(teaching_class)
        session.commit()

        resp = client.post('/api/schedule/run', json={
            'start_date': '2026-03-02',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'message' in data

    def test_get_schedule_results_with_filter(self, client, session):
        resp = client.get('/api/schedule/results?page=1&per_page=10')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'results' in data

    def test_adjust_schedule_not_found(self, client):
        resp = client.put('/api/schedule/adjust/99999', json={
            'day': 2,
            'period': 'afternoon',
        })
        assert resp.status_code == 404

    def test_adjust_schedule_empty_body(self, client, session):
        suffix = str(int(time.time() * 1000))
        room = Room(room_number=f'AR300_{suffix}', name=f'调整教室_{suffix}', capacity=50, room_type='普通教室')
        session.add(room)
        session.flush()

        tc = TeachingClass(
            course_id=99999,
            class_id=99999,
            teacher_id=99999,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(tc)
        session.flush()

        entry = ScheduleEntry(
            teaching_class_id=tc.id,
            week=1,
            day=1,
            period='morning',
            room_id=room.id,
        )
        session.add(entry)
        session.commit()

        resp = client.put(f'/api/schedule/adjust/{entry.id}', data=b'', content_type='application/json')
        assert resp.status_code in (400, 415)

    def test_check_conflict_not_found(self, client):
        resp = client.post('/api/schedule/check-conflict/99999', json={})
        assert resp.status_code == 404

    def test_check_conflict_empty(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT200_{suffix}', name=f'冲突教师_{suffix}')
        session.add(teacher)

        cls = Class(class_number=f'AC200_{suffix}', name=f'冲突班级_{suffix}', student_count=30)
        session.add(cls)
        session.flush()

        course = Course(
            course_number=f'ACR200_{suffix}',
            name=f'冲突课程_{suffix}',
            course_type='普通授课',
            teacher_id=teacher.id,
            class_id=cls.id,
        )
        session.add(course)
        session.flush()

        tc = TeachingClass(
            course_id=course.id,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(tc)
        session.commit()
        tc_id = tc.id

        resp = client.post(f'/api/schedule/check-conflict/{tc_id}', json={})
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'has_conflict' in data
        assert 'conflicts' in data

    def test_check_conflict_with_week_filter(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT201_{suffix}', name=f'冲突教师2_{suffix}')
        session.add(teacher)

        cls = Class(class_number=f'AC201_{suffix}', name=f'冲突班级2_{suffix}', student_count=30)
        session.add(cls)
        session.flush()

        course = Course(
            course_number=f'ACR201_{suffix}',
            name=f'冲突课程2_{suffix}',
            course_type='普通授课',
            teacher_id=teacher.id,
            class_id=cls.id,
        )
        session.add(course)
        session.flush()

        tc = TeachingClass(
            course_id=course.id,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(tc)
        session.commit()
        tc_id = tc.id

        resp = client.post(f'/api/schedule/check-conflict/{tc_id}', json={
            'week': 1,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['has_conflict'] is False

    def test_get_statistics(self, client):
        resp = client.get('/api/schedule/statistics')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_hours' in data
        assert 'total_sessions' in data
        assert 'completion_rate' in data

    def test_get_statistics_with_class_filter(self, client):
        resp = client.get('/api/schedule/statistics?class_id=1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_hours' in data

    def test_get_statistics_with_teacher_filter(self, client):
        resp = client.get('/api/schedule/statistics?teacher_id=1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_hours' in data

    def test_adjust_schedule_success(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT300_{suffix}', name=f'调整教师_{suffix}')
        session.add(teacher)

        cls = Class(class_number=f'AC300_{suffix}', name=f'调整班级_{suffix}', student_count=30)
        session.add(cls)
        session.flush()

        course = Course(
            course_number=f'ACR300_{suffix}',
            name=f'调整课程_{suffix}',
            course_type='普通授课',
            teacher_id=teacher.id,
            class_id=cls.id,
        )
        session.add(course)
        session.flush()

        room = Room(room_number=f'AR300_{suffix}', name=f'调整教室_{suffix}', capacity=50, room_type='普通教室')
        session.add(room)
        session.flush()

        tc = TeachingClass(
            course_id=course.id,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(tc)
        session.flush()

        entry = ScheduleEntry(
            teaching_class_id=tc.id,
            week=1,
            day=1,
            period='morning',
            room_id=room.id,
        )
        session.add(entry)
        session.commit()

        resp = client.put(f'/api/schedule/adjust/{entry.id}', json={
            'day': 2,
            'period': 'afternoon',
            'room_id': room.id,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['entry']['day'] == 2

    def test_adjust_schedule_room_conflict(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT301_{suffix}', name=f'调整教师2_{suffix}')
        session.add(teacher)

        cls = Class(class_number=f'AC301_{suffix}', name=f'调整班级2_{suffix}', student_count=30)
        session.add(cls)
        session.flush()

        course = Course(
            course_number=f'ACR301_{suffix}',
            name=f'调整课程2_{suffix}',
            course_type='普通授课',
            teacher_id=teacher.id,
            class_id=cls.id,
        )
        session.add(course)
        session.flush()

        room = Room(room_number=f'AR301_{suffix}', name=f'调整教室2_{suffix}', capacity=50, room_type='普通教室')
        session.add(room)
        session.flush()

        tc = TeachingClass(
            course_id=course.id,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(tc)
        session.flush()

        entry1 = ScheduleEntry(
            teaching_class_id=tc.id,
            week=1,
            day=1,
            period='morning',
            room_id=room.id,
        )
        session.add(entry1)

        tc2 = TeachingClass(
            course_id=999,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=2,
            assigned_period='afternoon',
        )
        session.add(tc2)
        session.flush()

        entry2 = ScheduleEntry(
            teaching_class_id=tc2.id,
            week=1,
            day=2,
            period='afternoon',
            room_id=room.id,
        )
        session.add(entry2)
        session.commit()

        resp = client.put(f'/api/schedule/adjust/{entry1.id}', json={
            'day': 2,
            'period': 'afternoon',
            'room_id': room.id,
        })
        assert resp.status_code == 400

    def test_adjust_schedule_teacher_conflict(self, client, session):
        suffix = str(int(time.time() * 1000))
        teacher = Teacher(teacher_number=f'AT302_{suffix}', name=f'调整教师3_{suffix}')
        session.add(teacher)

        cls = Class(class_number=f'AC302_{suffix}', name=f'调整班级3_{suffix}', student_count=30)
        session.add(cls)
        session.flush()

        course = Course(
            course_number=f'ACR302_{suffix}',
            name=f'调整课程3_{suffix}',
            course_type='普通授课',
            teacher_id=teacher.id,
            class_id=cls.id,
        )
        session.add(course)
        session.flush()

        room1 = Room(room_number=f'AR302_{suffix}', name=f'调整教室3_{suffix}', capacity=50, room_type='普通教室')
        room2 = Room(room_number=f'AR303_{suffix}', name=f'调整教室4_{suffix}', capacity=50, room_type='普通教室')
        session.add_all([room1, room2])
        session.flush()

        tc = TeachingClass(
            course_id=course.id,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=1,
            assigned_period='morning',
        )
        session.add(tc)
        session.flush()

        entry1 = ScheduleEntry(
            teaching_class_id=tc.id,
            week=1,
            day=1,
            period='morning',
            room_id=room1.id,
        )
        session.add(entry1)

        tc2 = TeachingClass(
            course_id=999,
            class_id=cls.id,
            teacher_id=teacher.id,
            assigned_day=2,
            assigned_period='afternoon',
        )
        session.add(tc2)
        session.flush()

        entry2 = ScheduleEntry(
            teaching_class_id=tc2.id,
            week=1,
            day=2,
            period='afternoon',
            room_id=room2.id,
        )
        session.add(entry2)
        session.commit()

        resp = client.put(f'/api/schedule/adjust/{entry1.id}', json={
            'day': 2,
            'period': 'afternoon',
            'room_id': room2.id,
        })
        assert resp.status_code == 400
