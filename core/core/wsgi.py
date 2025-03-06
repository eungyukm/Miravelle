"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line # 메모리 기반 SQLite 사용 (추후에 PostgreSQL로 전환 권장)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# 서버 시작시 마이그레이션 자동 실행
# 메모리 기반 SQLite 사용 시 필요 (추후에 PostgreSQL로 전환 권장)
application = get_wsgi_application()
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
