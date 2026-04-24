"""测试运行脚本"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))


def run_tests(test_files=None, verbose=False, pattern=None):
    """运行测试"""
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'testing'

    test_dir = os.path.join(os.path.dirname(__file__), 'tests')

    if test_files:
        args = ['-v'] if verbose else []
        for f in test_files:
            full_path = os.path.join(test_dir, f)
            if os.path.exists(full_path):
                args.append(full_path)
            else:
                print(f"警告: 测试文件 {f} 不存在")
    else:
        args = [test_dir, '-v'] if verbose else [test_dir]

    if pattern:
        args.extend(['-k', pattern])

    import pytest
    exit_code = pytest.main(args)
    return exit_code


def run_with_coverage():
    """运行测试并生成覆盖率报告"""
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'testing'

    test_dir = os.path.join(os.path.dirname(__file__), 'tests')

    try:
        import pytest_cov
        args = [
            test_dir, '-v',
            '--cov=.',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
        ]
        exit_code = pytest.main(args)
        print("\n覆盖率报告已生成到 htmlcov/index.html")
        return exit_code
    except ImportError:
        print("警告: pytest-cov 未安装，运行普通测试")
        print("安装命令: pip install pytest-cov")
        return run_tests()


def list_tests():
    """列出所有可用测试"""
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    import pytest
    args = [test_dir, '--collect-only', '-q']
    pytest.main(args)


def main():
    parser = argparse.ArgumentParser(description='排课系统测试运行器')
    parser.add_argument(
        'action',
        nargs='?',
        default='run',
        choices=['run', 'coverage', 'list'],
        help='操作: run(运行测试), coverage(运行测试+覆盖率), list(列出测试)'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='指定测试文件'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细输出'
    )
    parser.add_argument(
        '-k', '--pattern',
        help='测试名称过滤模式'
    )

    args = parser.parse_args()

    if args.action == 'run':
        exit_code = run_tests(args.files, args.verbose, args.pattern)
    elif args.action == 'coverage':
        exit_code = run_with_coverage()
    elif args.action == 'list':
        list_tests()
        exit_code = 0
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
