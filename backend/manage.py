#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# 获取 manage.py 所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 添加 db_backends 路径到 sys.path 中
sys.path.append(os.path.join(BASE_DIR, 'db_backends'))

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
