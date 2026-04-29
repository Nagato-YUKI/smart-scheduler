import os
import sys
import random
import argparse
from datetime import datetime, timedelta
import json
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from peewee_manager import (
    Room, Teacher, SchoolClass, Course, Holiday, TeachingClass, ScheduleEntry, _database
)
from config import Config


def create_tables(drop_first=False):
    _database.init(Config.DATABASE)
    _database.connect()
    if drop_first:
        print('删除现有表...')
        _database.drop_tables([ScheduleEntry, TeachingClass, Course, Holiday, SchoolClass, Teacher, Room], safe=True)
    print('创建数据库表...')
    _database.create_tables([Room, Teacher, SchoolClass, Course, Holiday, TeachingClass, ScheduleEntry], safe=True)
    print('表创建完成。')


def insert_sample_data():
    _database.drop_tables([ScheduleEntry, TeachingClass, Course, Holiday, SchoolClass, Teacher, Room], safe=True)
    _database.create_tables([Room, Teacher, SchoolClass, Course, Holiday, TeachingClass, ScheduleEntry], safe=True)

    print('插入测试数据...')

    # === 教室 (30间) ===
    rooms_data = [
        ('R001', '博学楼101', 60, '普通教室'), ('R002', '博学楼102', 55, '普通教室'),
        ('R003', '博学楼201', 50, '多媒体教室'), ('R004', '博学楼202', 45, '多媒体教室'),
        ('R005', '博学楼301', 40, '机房'), ('R006', '博学楼302', 40, '机房'),
        ('R007', '博学楼401', 35, '实验室'), ('R008', '博学楼402', 30, '实验室'),
        ('R009', '致知楼101', 65, '普通教室'), ('R010', '致知楼102', 60, '普通教室'),
        ('R011', '致知楼201', 50, '多媒体教室'), ('R012', '致知楼202', 48, '多媒体教室'),
        ('R013', '致知楼301', 42, '机房'), ('R014', '致知楼302', 38, '机房'),
        ('R015', '致知楼401', 32, '实验室'), ('R016', '明理楼101', 70, '普通教室'),
        ('R017', '明理楼102', 65, '普通教室'), ('R018', '明理楼201', 55, '多媒体教室'),
        ('R019', '明理楼301', 45, '机房'), ('R020', '明理楼401', 35, '实验室'),
        ('R021', '笃行楼101', 50, '普通教室'), ('R022', '笃行楼102', 48, '普通教室'),
        ('R023', '笃行楼201', 45, '多媒体教室'), ('R024', '笃行楼301', 40, '机房'),
        ('R025', '笃行楼302', 38, '机房'), ('R026', '笃行楼401', 32, '实验室'),
        ('R027', '厚德楼101', 60, '普通教室'), ('R028', '厚德楼201', 50, '多媒体教室'),
        ('R029', '厚德楼301', 42, '机房'), ('R030', '厚德楼401', 35, '实验室'),
    ]
    rooms = []
    for number, name, cap, rtype in rooms_data:
        rooms.append(Room.create(room_number=number, name=name, capacity=cap, room_type=rtype))

    # === 教师 (25名, 每人最多6个班, 共150个教学班容量) ===
    teachers_data = [
        ('T001', '张伟', ['高等数学', '线性代数'], 6),
        ('T002', '李娜', ['大学英语', '通信原理'], 6),
        ('T003', '王强', ['大学物理', '数字信号处理'], 6),
        ('T004', '刘洋', ['计算机基础', 'C语言程序设计'], 6),
        ('T005', '陈明', ['数据结构', '算法设计与分析'], 6),
        ('T006', '赵敏', ['操作系统'], 6),
        ('T007', '孙丽', ['数据库原理'], 6),
        ('T008', '周杰', ['网络工程', '网络安全'], 6),
        ('T009', '吴芳', ['软件工程', '云计算技术'], 6),
        ('T010', '郑华', ['人工智能导论', '机器学习'], 6),
        ('T011', '冯刚', ['编译原理'], 6),
        ('T012', '何静', ['离散数学'], 6),
        ('T013', '许明', ['概率论与数理统计'], 6),
        ('T014', '马超', ['计算机组成原理'], 6),
        ('T015', '林涛', ['嵌入式系统', '物联网技术'], 6),
        ('T016', '黄磊', ['高等数学', '复变函数'], 6),
        ('T017', '周婷', ['大学英语', '英语写作'], 6),
        ('T018', '吴鹏', ['大学物理', '量子力学'], 6),
        ('T019', '郑敏', ['数据结构', '图论'], 6),
        ('T020', '王芳', ['操作系统', '嵌入式系统'], 6),
        ('T021', '陈刚', ['计算机网络', '信息安全'], 6),
        ('T022', '李华', ['数据库原理', '大数据技术'], 6),
        ('T023', '张丽', ['机器学习', '深度学习'], 6),
        ('T024', '刘敏', ['软件工程', '软件测试'], 6),
        ('T025', '赵强', ['编译原理', '计算机组成原理'], 6),
    ]
    teachers = []
    for number, name, courses, max_w in teachers_data:
        teachers.append(Teacher.create(
            teacher_number=number, name=name,
            teachable_courses=json.dumps(courses),
            max_weekly_sessions=max_w
        ))

    # === 班级 (20个系 × 2班 = 40班) ===
    departments = [
        '计算机科学与技术', '软件工程', '网络工程', '信息安全', '人工智能',
        '数据科学与大数据技术', '电子信息工程', '通信工程', '自动化', '物联网工程',
        '数字媒体技术', '智能科学与技术', '空间信息与数字技术', '网络空间安全', '区块链工程',
        '元宇宙工程', '量子信息科学', '集成电路设计与集成系统', '机器人工程', '虚拟现实技术'
    ]
    classes = []
    for dept in departments:
        for j in range(1, 3):
            cls = SchoolClass.create(
                class_number=f'C{len(classes)+1:03d}',
                name=f'{dept}{j}班',
                student_count=random.randint(35, 48),
                department=dept
            )
            classes.append(cls)

    # === 课程池 (26门课程, 25位教师) ===
    course_pool = [
        ('高等数学', '普通授课', 0),
        ('线性代数', '普通授课', 0),
        ('概率论与数理统计', '普通授课', 12),
        ('离散数学', '普通授课', 11),
        ('大学物理', '普通授课', 2),
        ('大学英语', '普通授课', 1),
        ('计算机基础', '上机', 3),
        ('C语言程序设计', '上机', 3),
        ('数据结构', '上机', 4),
        ('算法设计与分析', '上机', 4),
        ('操作系统', '上机', 5),
        ('计算机网络', '上机', 20),
        ('数据库原理', '上机', 6),
        ('软件工程', '普通授课', 8),
        ('编译原理', '普通授课', 10),
        ('计算机组成原理', '普通授课', 13),
        ('嵌入式系统', '实验', 14),
        ('人工智能导论', '上机', 9),
        ('网络安全', '实验', 7),
        ('云计算技术', '上机', 8),
        ('机器学习', '上机', 9),
        ('数字信号处理', '实验', 2),
        ('通信原理', '普通授课', 1),
        ('物联网技术', '实验', 14),
        ('复变函数', '普通授课', 15),
        ('量子力学', '普通授课', 17),
    ]

    # === 为每个班级分配4门课程 (40班×4=160个教学班, 150容量会有限制) ===
    courses = []
    tc_list = []
    random.seed(42)

    teacher_class_count = defaultdict(int)
    teacher_max_classes = {t.id: t.max_weekly_sessions for t in teachers}

    for cls in classes:
        cls_courses = []
        selected_indices = set(random.sample(range(len(course_pool)), 4))
        for idx in selected_indices:
            name, ctype, teacher_idx = course_pool[idx]
            teacher = teachers[teacher_idx]
            cls_courses.append((name, ctype, teacher, idx))

        cls_courses.sort(key=lambda x: teacher_class_count.get(x[2].id, 0))

        for name, ctype, teacher, idx in cls_courses:
            if teacher_class_count[teacher.id] >= teacher_max_classes[teacher.id]:
                alternative_found = False
                for alt_idx in range(len(course_pool)):
                    if alt_idx in selected_indices:
                        continue
                    alt_name, alt_ctype, alt_teacher_idx = course_pool[alt_idx]
                    alt_teacher = teachers[alt_teacher_idx]
                    if any(c[0] == alt_name for c in cls_courses):
                        continue
                    if teacher_class_count[alt_teacher.id] < teacher_max_classes[alt_teacher.id]:
                        name, ctype, teacher = alt_name, alt_ctype, alt_teacher
                        selected_indices.add(alt_idx)
                        alternative_found = True
                        break
                if not alternative_found:
                    continue

            course = Course.create(
                course_number=f'CR{len(courses)+1:03d}',
                name=name,
                course_type=ctype,
                teacher=teacher,
                school_class=cls,
                total_hours=45
            )
            courses.append(course)
            tc = TeachingClass.create(
                course=course,
                school_class=cls,
                teacher=teacher,
                assigned_day=0,
                assigned_period='',
            )
            tc_list.append(tc)
            teacher_class_count[teacher.id] += 1

    print(f'创建了 {len(tc_list)} 个教学班')
    print('教师负载分布:')
    for t in teachers:
        count = teacher_class_count[t.id]
        max_c = teacher_max_classes[t.id]
        status = '满' if count >= max_c else f'{count}/{max_c}'
        print(f'  {t.name} ({t.teacher_number}): {status}')

    # === 节假日: 2026年9月~2027年2月 (下半学期) ===
    holiday_data = [
        ('2026-09-27', '中秋节'),
        ('2026-10-01', '国庆节'), ('2026-10-02', '国庆节'), ('2026-10-03', '国庆节'),
        ('2026-10-04', '国庆节'), ('2026-10-05', '国庆节'), ('2026-10-06', '国庆节'),
        ('2026-10-07', '国庆节'),
        ('2027-01-01', '元旦'), ('2027-01-02', '元旦'), ('2027-01-03', '元旦'),
        ('2027-02-16', '春节'), ('2027-02-17', '春节'), ('2027-02-18', '春节'),
        ('2027-02-19', '春节'), ('2027-02-20', '春节'), ('2027-02-21', '春节'),
        ('2027-02-22', '春节'),
    ]
    for date_str, name in holiday_data:
        Holiday.create(date=datetime.strptime(date_str, '%Y-%m-%d'), name=name)

    # === 排课算法 ===
    semester_start = datetime(2026, 9, 7)
    period_hours = {'morning': 4, 'afternoon': 4, 'evening': 3}

    holiday_dates = set()
    for h in Holiday.select():
        holiday_dates.add(h.date)

    holiday_week_day = set()
    for week in range(1, 17):
        for day in range(1, 6):
            d = semester_start + timedelta(days=(week - 1) * 7 + day - 1)
            if d.date() in holiday_dates:
                holiday_week_day.add((week, day))

    normal_rooms = sorted(
        [r for r in rooms if r.room_type in ('普通教室', '多媒体教室')],
        key=lambda r: r.capacity
    )

    teacher_slot_used = defaultdict(set)
    room_slot_used = {}
    class_slot_used = defaultdict(set)
    dp_usage_count = defaultdict(int)

    all_day_periods = []
    for d in range(1, 6):
        for p in ['morning', 'afternoon', 'evening']:
            all_day_periods.append((d, p))

    # 强制约1/3课程排晚上
    evening_target = len(tc_list) // 3
    evening_count = 0

    scheduled_count = 0
    fail_count = 0

    for tc in tc_list:
        cls = tc.school_class
        teacher = tc.teacher
        target_hours = tc.course.total_hours

        teacher_used_dps = set()
        for (w, d, p) in teacher_slot_used[teacher.id]:
            teacher_used_dps.add((d, p))

        best_dp = None
        best_weeks = []
        best_hours = 0
        best_score = float('inf')

        for day_num, period in all_day_periods:
            if (day_num, period) in teacher_used_dps:
                continue

            hps = period_hours[period]
            weeks_possible = []

            for week in range(1, 17):
                if (week, day_num) in holiday_week_day:
                    continue
                if (week, day_num, period) in teacher_slot_used[teacher.id]:
                    continue
                if (week, day_num, period) in class_slot_used[cls.id]:
                    continue
                weeks_possible.append(week)

            possible_hours = len(weeks_possible) * hps
            if possible_hours < target_hours:
                continue

            # 评分：越少用的(day,period)越好；晚上时段在数量不足时有负分奖励
            usage = dp_usage_count[(day_num, period)]
            if period == 'evening' and evening_count < evening_target:
                evening_bonus = -20
            else:
                evening_bonus = 0
            score = usage * 10 + evening_bonus

            if score < best_score:
                best_hours = possible_hours
                best_weeks = weeks_possible
                best_dp = (day_num, period, hps)
                best_score = score

        if best_dp and best_hours >= target_hours:
            day_num, period, hps = best_dp
            dp_usage_count[(day_num, period)] += 1
            if period == 'evening':
                evening_count += 1

            suitable_rooms = [r for r in rooms if r.room_type in ('普通教室', '多媒体教室', '机房', '实验室') and r.capacity >= cls.student_count] or rooms
            room = suitable_rooms[scheduled_count % len(suitable_rooms)]

            hours_scheduled = 0
            for week in best_weeks:
                if hours_scheduled >= target_hours:
                    break

                room_key = (week, day_num, period, room.id)
                if room_key in room_slot_used:
                    alt_rooms = [r for r in suitable_rooms if (week, day_num, period, r.id) not in room_slot_used]
                    if alt_rooms:
                        room = alt_rooms[0]
                        room_key = (week, day_num, period, room.id)
                    else:
                        continue

                ScheduleEntry.create(
                    teaching_class=tc,
                    week=week,
                    day=day_num,
                    period=period,
                    room=room,
                    is_holiday=False,
                )
                room_slot_used[room_key] = True
                teacher_slot_used[teacher.id].add((week, day_num, period))
                class_slot_used[cls.id].add((week, day_num, period))
                hours_scheduled += hps

            if hours_scheduled >= target_hours:
                print(f'  [OK] {tc.course.name:16s} - {tc.school_class.name:20s}: {hours_scheduled}课时 ({period})')
                scheduled_count += 1
            elif hours_scheduled > 0:
                print(f'  [WARN] {tc.course.name:16s} - {tc.school_class.name:20s}: {hours_scheduled}课时')
                scheduled_count += 1
            else:
                print(f'  [FAIL] {tc.course.name:16s} - {tc.school_class.name:20s}: 0课时')
                fail_count += 1
        else:
            print(f'  [FAIL] {tc.course.name:16s} - {tc.school_class.name:20s}: 0课时')
            fail_count += 1

    # 统计
    period_hours_map = {'morning': 4, 'afternoon': 4, 'evening': 3}
    ok_count = 0
    warn_count = 0
    fail_c = 0
    evening_total = 0
    morning_total = 0
    afternoon_total = 0
    for tc in tc_list:
        target = tc.course.total_hours
        entries = list(ScheduleEntry.select().where(ScheduleEntry.teaching_class == tc))
        actual_hours = 0
        if entries:
            actual_hours = sum(period_hours_map.get(e.period, 4) for e in entries)
            for e in entries:
                if e.period == 'evening':
                    evening_total += 1
                elif e.period == 'morning':
                    morning_total += 1
                else:
                    afternoon_total += 1
        if actual_hours >= target:
            ok_count += 1
        elif actual_hours > 0:
            warn_count += 1
        else:
            fail_c += 1

    total_entries = ScheduleEntry.select().count()
    print(f'\n测试数据插入完成。')
    print(f'  教室: {Room.select().count()} 间')
    print(f'  教师: {Teacher.select().count()} 名')
    print(f'  班级: {SchoolClass.select().count()} 个')
    print(f'  课程: {Course.select().count()} 门')
    print(f'  教学班: {TeachingClass.select().count()} 个')
    print(f'  已排课成功: {ok_count} 个')
    print(f'  已排课部分: {warn_count} 个')
    print(f'  未排课: {fail_c} 个')
    print(f'  课表记录: {total_entries} 条')
    print(f'  节假日: {Holiday.select().count()} 天')
    print(f'  上午课时次数: {morning_total}')
    print(f'  下午课时次数: {afternoon_total}')
    print(f'  晚上课时次数: {evening_total}')


def main():
    parser = argparse.ArgumentParser(description='排课系统数据库初始化工具')
    parser.add_argument('--drop', action='store_true', help='删除现有表后重新创建')
    args = parser.parse_args()
    try:
        create_tables(drop_first=True)
        insert_sample_data()
        print('数据库初始化完成。')
    except Exception as e:
        print(f'初始化失败: {e}')
        import traceback
        traceback.print_exc()
    finally:
        if not _database.is_closed():
            _database.close()


if __name__ == '__main__':
    main()
