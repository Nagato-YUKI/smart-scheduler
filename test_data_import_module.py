# -*- coding: utf-8 -*-
"""
数据导入模块全面测试脚本
测试范围：
1. 后端API测试（模板下载、综合导入）
2. 排课功能测试
3. 清空数据功能测试
"""

import requests
import json
import os
from datetime import datetime

# 测试配置
BACKEND_URL = "http://127.0.0.1:5000"
FRONTEND_URL = "http://localhost:3000"
TEST_DATA_FILE = r"e:\trae project\paike\backend\排课测试数据_综合.xlsx"

# 测试结果收集
test_results = {
    "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "通过": 0,
    "失败": 0,
    "测试项": []
}


def add_result(name, passed, message, details=None):
    """记录测试结果"""
    status = "通过" if passed else "失败"
    test_results["测试项"].append({
        "名称": name,
        "状态": status,
        "消息": message,
        "详情": details
    })
    if passed:
        test_results["通过"] += 1
    else:
        test_results["失败"] += 1

    prefix = "[PASS]" if passed else "[FAIL]"
    print(f"{prefix} {name}: {message}")
    if details:
        for k, v in details.items():
            print(f"      {k}: {v}")


def test_backend_health():
    """测试后端服务健康状态"""
    print("\n" + "="*60)
    print("1. 后端服务健康检查")
    print("="*60)

    try:
        r = requests.get(f"{BACKEND_URL}/api/rooms", timeout=5)
        if r.status_code == 200:
            add_result("后端API健康检查", True, f"后端服务正常响应 (HTTP {r.status_code})")
            return True
        else:
            add_result("后端API健康检查", False, f"后端返回异常状态码: {r.status_code}")
            return False
    except Exception as e:
        add_result("后端API健康检查", False, f"后端服务无法连接: {str(e)}")
        return False


def test_template_download():
    """测试模板下载API"""
    print("\n" + "="*60)
    print("2. 模板下载API测试")
    print("="*60)

    # 测试综合模板下载
    try:
        r = requests.get(f"{BACKEND_URL}/api/import/template/comprehensive", timeout=10)
        if r.status_code == 200:
            content_type = r.headers.get('Content-Type', '')
            if 'spreadsheetml' in content_type or 'octet-stream' in content_type:
                add_result("综合模板下载", True, f"成功下载综合模板 (大小: {len(r.content)} bytes)")
            else:
                add_result("综合模板下载", False, f"响应Content-Type异常: {content_type}")
        else:
            add_result("综合模板下载", False, f"HTTP错误: {r.status_code}")
    except Exception as e:
        add_result("综合模板下载", False, f"请求失败: {str(e)}")

    # 测试单个类型模板下载
    for data_type in ['room', 'teacher', 'class', 'course']:
        try:
            r = requests.get(f"{BACKEND_URL}/api/import/template/{data_type}", timeout=10)
            if r.status_code == 200:
                add_result(f"{data_type}模板下载", True, f"成功下载{data_type}模板")
            else:
                add_result(f"{data_type}模板下载", False, f"HTTP错误: {r.status_code}")
        except Exception as e:
            add_result(f"{data_type}模板下载", False, f"请求失败: {str(e)}")


def get_current_data_counts():
    """获取当前各表数据量"""
    counts = {}
    try:
        # 获取教室数量
        r = requests.get(f"{BACKEND_URL}/api/rooms", timeout=5)
        if r.status_code == 200:
            counts['rooms'] = len(r.json())

        # 获取教师数量
        r = requests.get(f"{BACKEND_URL}/api/teachers", timeout=5)
        if r.status_code == 200:
            counts['teachers'] = len(r.json())

        # 获取班级数量
        r = requests.get(f"{BACKEND_URL}/api/classes", timeout=5)
        if r.status_code == 200:
            counts['classes'] = len(r.json())

        # 获取课程数量
        r = requests.get(f"{BACKEND_URL}/api/courses", timeout=5)
        if r.status_code == 200:
            counts['courses'] = len(r.json())

        # 获取节假日数量
        r = requests.get(f"{BACKEND_URL}/api/holidays", timeout=5)
        if r.status_code == 200:
            counts['holidays'] = len(r.json())

        # 获取排课记录数量
        r = requests.get(f"{BACKEND_URL}/api/schedule/results?per_page=1", timeout=5)
        if r.status_code == 200:
            counts['schedule_entries'] = r.json().get('total', 0)

    except Exception as e:
        print(f"获取数据量失败: {e}")

    return counts


def test_comprehensive_import():
    """测试综合导入功能"""
    print("\n" + "="*60)
    print("3. 综合导入API测试")
    print("="*60)

    # 检查测试文件是否存在
    if not os.path.exists(TEST_DATA_FILE):
        add_result("综合导入测试", False, f"测试数据文件不存在: {TEST_DATA_FILE}")
        return False

    # 先清空所有数据
    print("  -> 清空现有数据...")
    try:
        r = requests.post(f"{BACKEND_URL}/api/schedule/clear-all", timeout=10)
        if r.status_code != 200:
            print(f"  -> 清空数据失败: {r.status_code}")
    except Exception as e:
        print(f"  -> 清空数据异常: {e}")

    before_counts = get_current_data_counts()
    print(f"  -> 清空后数据状态: {before_counts}")

    # 执行综合导入
    print(f"  -> 上传测试文件: {TEST_DATA_FILE}")
    try:
        with open(TEST_DATA_FILE, 'rb') as f:
            files = {'file': ('排课测试数据_综合.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {'type': 'comprehensive'}
            r = requests.post(f"{BACKEND_URL}/api/import/upload", files=files, data=data, timeout=30)

        if r.status_code in [200, 207]:  # 207 Multi-Status 表示部分成功
            result = r.json()
            print(f"  -> 导入响应: {json.dumps(result, ensure_ascii=False)}")

            # 验证导入结果
            if 'count' in result:
                total_imported = result.get('count', 0)
                details = result.get('details', {})

                # 检查各类数据导入情况
                room_imp = details.get('room', {}).get('imported', 0)
                room_upd = details.get('room', {}).get('updated', 0)
                teacher_imp = details.get('teacher', {}).get('imported', 0)
                teacher_upd = details.get('teacher', {}).get('updated', 0)
                class_imp = details.get('class', {}).get('imported', 0)
                class_upd = details.get('class', {}).get('updated', 0)
                holiday_imp = details.get('holiday', {}).get('imported', 0)
                course_imp = details.get('course', {}).get('imported', 0)
                course_upd = details.get('course', {}).get('updated', 0)

                add_result("综合导入测试", True,
                          f"成功导入 {total_imported} 条数据",
                          {
                              "教室": f"新增{room_imp}+更新{room_upd}",
                              "教师": f"新增{teacher_imp}+更新{teacher_upd}",
                              "班级": f"新增{class_imp}+更新{class_upd}",
                              "节假日": f"导入{holiday_imp}天",
                              "课程": f"新增{course_imp}+更新{course_upd}"
                          })

                # 验证节假日数据
                if holiday_imp > 0:
                    add_result("节假日数据验证", True, f"节假日数据导入成功 ({holiday_imp}天)")
                else:
                    add_result("节假日数据验证", False, "节假日数据未导入")

                # 验证数据库中的实际数据
                after_counts = get_current_data_counts()
                print(f"  -> 导入后数据状态: {after_counts}")

                return True
            else:
                add_result("综合导入测试", False, f"响应格式异常: {result}")
                return False
        else:
            add_result("综合导入测试", False, f"HTTP错误: {r.status_code}, 响应: {r.text}")
            return False

    except Exception as e:
        add_result("综合导入测试", False, f"请求失败: {str(e)}")
        return False


def test_schedule_run():
    """测试排课功能"""
    print("\n" + "="*60)
    print("4. 排课功能测试")
    print("="*60)

    # 执行排课
    print("  -> 执行排课...")
    try:
        r = requests.post(f"{BACKEND_URL}/api/schedule/run", timeout=60)
        if r.status_code == 200:
            result = r.json()
            print(f"  -> 排课响应: {json.dumps(result, ensure_ascii=False)}")

            success_count = result.get('success_count', 0)
            total_entries = result.get('total_entries', 0)

            add_result("排课执行", True,
                      f"排课完成 (成功{success_count}条, 总记录{total_entries}条)",
                      result)

            return True
        else:
            add_result("排课执行", False, f"HTTP错误: {r.status_code}, 响应: {r.text}")
            return False
    except Exception as e:
        add_result("排课执行", False, f"请求失败: {str(e)}")
        return False


def test_evening_schedule():
    """测试晚上时段排课"""
    print("\n" + "="*60)
    print("5. 晚上时段排课验证")
    print("="*60)

    try:
        # 获取统计数据
        r = requests.get(f"{BACKEND_URL}/api/schedule/statistics", timeout=10)
        if r.status_code == 200:
            stats = r.json()
            period_dist = stats.get('period_distribution', {})
            morning_hours = period_dist.get('morning', 0)
            afternoon_hours = period_dist.get('afternoon', 0)
            evening_hours = period_dist.get('evening', 0)

            total_hours = morning_hours + afternoon_hours + evening_hours

            print(f"  -> 时段分布统计:")
            print(f"     上午: {morning_hours}课时 ({morning_hours/total_hours*100:.1f}%)" if total_hours > 0 else "     上午: 0课时 (0%)")
            print(f"     下午: {afternoon_hours}课时 ({afternoon_hours/total_hours*100:.1f}%)" if total_hours > 0 else "     下午: 0课时 (0%)")
            print(f"     晚上: {evening_hours}课时 ({evening_hours/total_hours*100:.1f}%)" if total_hours > 0 else "     晚上: 0课时 (0%)")

            add_result("晚上时段排课验证", evening_hours > 0,
                      f"晚上时段排了 {evening_hours} 课时" if evening_hours > 0 else "晚上时段无排课",
                      {
                          "上午课时": morning_hours,
                          "下午课时": afternoon_hours,
                          "晚上课时": evening_hours,
                          "总课时": total_hours,
                          "晚上占比": f"{evening_hours/total_hours*100:.1f}%" if total_hours > 0 else "0%"
                      })

            # 验证排课完整性
            total_classes = stats.get('total_classes', 0)
            scheduled_classes = stats.get('scheduled_classes', 0)
            completion_rate = stats.get('completion_rate', 0)

            add_result("排课完成率", completion_rate >= 80,
                      f"排课完成率: {completion_rate}%",
                      {
                          "总课程数": total_classes,
                          "已排课程数": scheduled_classes,
                          "完成率": f"{completion_rate}%"
                      })

            return True
        else:
            add_result("晚上时段排课验证", False, f"获取统计失败: {r.status_code}")
            return False
    except Exception as e:
        add_result("晚上时段排课验证", False, f"请求失败: {str(e)}")
        return False


def test_clear_entries():
    """测试清空排课（保留基础数据）"""
    print("\n" + "="*60)
    print("6. 清空排课功能测试 (clear-entries)")
    print("="*60)

    # 先确保有排课数据
    print("  -> 检查当前排课数据...")
    try:
        r = requests.get(f"{BACKEND_URL}/api/schedule/results?per_page=1", timeout=10)
        if r.status_code == 200:
            before_total = r.json().get('total', 0)
            print(f"  -> 当前排课记录数: {before_total}")

            if before_total == 0:
                print("  -> 当前无排课记录，先执行排课...")
                requests.post(f"{BACKEND_URL}/api/schedule/run", timeout=60)
                r = requests.get(f"{BACKEND_URL}/api/schedule/results?per_page=1", timeout=10)
                before_total = r.json().get('total', 0)
                print(f"  -> 排课后记录数: {before_total}")
    except Exception as e:
        print(f"  -> 检查排课数据失败: {e}")

    # 获取清空前的基础数据数量
    before_counts = get_current_data_counts()
    print(f"  -> 清空前数据: {before_counts}")

    # 执行清空排课
    print("  -> 执行清空排课 (clear-entries)...")
    try:
        r = requests.post(f"{BACKEND_URL}/api/schedule/clear-entries", timeout=10)
        if r.status_code == 200:
            result = r.json()
            print(f"  -> 清空响应: {json.dumps(result, ensure_ascii=False)}")

            deleted_count = result.get('deleted_count', 0)

            # 获取清空后的数据
            after_counts = get_current_data_counts()
            print(f"  -> 清空后数据: {after_counts}")

            # 验证基础数据是否保留
            rooms_kept = after_counts.get('rooms', 0) > 0
            teachers_kept = after_counts.get('teachers', 0) > 0
            classes_kept = after_counts.get('classes', 0) > 0
            courses_kept = after_counts.get('courses', 0) > 0
            holidays_kept = after_counts.get('holidays', 0) > 0

            schedule_cleared = after_counts.get('schedule_entries', 0) == 0

            add_result("清空排课记录", schedule_cleared,
                      f"已清空 {deleted_count} 条排课记录" if schedule_cleared else "排课记录未清空",
                      {
                          "已删除记录数": deleted_count,
                          "排课记录已清空": schedule_cleared
                      })

            add_result("基础数据保留验证", rooms_kept and teachers_kept and classes_kept and courses_kept and holidays_kept,
                      "基础数据（教室、教师、班级、课程、节假日）均已保留" if (rooms_kept and teachers_kept and classes_kept and courses_kept and holidays_kept) else "部分基础数据丢失",
                      {
                          "教室保留": rooms_kept,
                          "教师保留": teachers_kept,
                          "班级保留": classes_kept,
                          "课程保留": courses_kept,
                          "节假日保留": holidays_kept
                      })

            return True
        else:
            add_result("清空排课记录", False, f"HTTP错误: {r.status_code}")
            return False
    except Exception as e:
        add_result("清空排课记录", False, f"请求失败: {str(e)}")
        return False


def test_holiday_import():
    """测试节假日数据导入"""
    print("\n" + "="*60)
    print("7. 节假日数据验证")
    print("="*60)

    try:
        r = requests.get(f"{BACKEND_URL}/api/holidays", timeout=10)
        if r.status_code == 200:
            holidays = r.json()
            print(f"  -> 节假日列表 ({len(holidays)}条):")
            for h in holidays[:5]:  # 只显示前5条
                print(f"     - {h.get('date')}: {h.get('name')}")
            if len(holidays) > 5:
                print(f"     ... 还有 {len(holidays) - 5} 条")

            if len(holidays) > 0:
                add_result("节假日数据存在", True, f"成功导入 {len(holidays)} 个节假日")
            else:
                add_result("节假日数据存在", False, "没有导入节假日数据")
        else:
            add_result("节假日数据存在", False, f"获取节假日失败: {r.status_code}")
    except Exception as e:
        add_result("节假日数据存在", False, f"请求失败: {str(e)}")


def test_all_data_types():
    """验证所有数据类型都已导入"""
    print("\n" + "="*60)
    print("8. 全数据类型导入验证")
    print("="*60)

    counts = get_current_data_counts()
    print(f"  -> 当前数据量: {counts}")

    all_imported = True
    details = {}

    for data_type, count in counts.items():
        if data_type == 'schedule_entries':
            continue
        details[data_type] = count
        if count == 0:
            all_imported = False

    add_result("全数据类型导入", all_imported,
              "所有数据类型（教室、教师、班级、课程、节假日）都已导入" if all_imported else "部分数据类型未导入",
              details)


def main():
    """主测试流程"""
    print("\n" + "#"*60)
    print("# 数据导入模块全面测试")
    print("#"*60)

    # 1. 后端健康检查
    if not test_backend_health():
        print("\n后端服务不可用，测试终止。")
        return

    # 2. 模板下载测试
    test_template_download()

    # 3. 综合导入测试
    if not test_comprehensive_import():
        print("\n综合导入失败，后续测试可能受影响。")

    # 4. 节假日数据验证
    test_holiday_import()

    # 5. 全数据类型验证
    test_all_data_types()

    # 6. 排课测试
    if not test_schedule_run():
        print("\n排课失败，跳过晚上时段验证。")
    else:
        # 7. 晚上时段排课验证
        test_evening_schedule()

    # 8. 清空排课测试
    test_clear_entries()

    # 输出测试报告
    print("\n" + "#"*60)
    print("# 测试报告")
    print("#"*60)
    print(f"\n测试时间: {test_results['测试时间']}")
    print(f"通过: {test_results['通过']} 项")
    print(f"失败: {test_results['失败']} 项")
    print(f"总计: {test_results['通过'] + test_results['失败']} 项")

    print("\n详细结果:")
    for item in test_results['测试项']:
        status_icon = "✓" if item['状态'] == '通过' else "✗"
        print(f"  [{status_icon}] {item['名称']}: {item['状态']}")
        if item['详情']:
            for k, v in item['详情'].items():
                print(f"       - {k}: {v}")

    # 保存测试报告
    report_file = r"e:\trae project\paike\test_results\data_import_test_report.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    print(f"\n测试报告已保存: {report_file}")

    # 返回测试结果
    return test_results['失败'] == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
