import os

DEBUG = True

ALLOWED_HOSTS = ["*"]

# PostgreSQL 配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'oj_db'),
        'USER': os.getenv('POSTGRES_USER', 'oj_admin'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'ojoj_admin123'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Redis 配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv('REDIS_HOST', 'redis://localhost:6379/'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.getenv('REDIS_PASSWORD', 'judgeme_114514!')
        }
    }
}

# celery 配置
CELERY_BROKER_URL = os.getenv('CELERY_REDIS_HOST', 'redis://:judgeme_114514!@localhost:6379/')
CELERY_RESULT_BACKEND = os.getenv('CELERY_REDIS_HOST', 'redis://:judgeme_114514!@localhost:6379/')
# 可接受的内容格式
CELERY_ACCEPT_CONTENT = ["json"]
# 任务序列化数据格式
CELERY_TASK_SERIALIZER = "json"
# 结果序列化数据格式
CELERY_RESULT_SERIALIZER = "json"
CELERYD_TIME_LIMIT = 60
CELERY_TASK_TRACK_STARTED = True

# 判题机认证与授权Header
AUTHN_HEADER = os.getenv('AUTHN_HEADER', 'X-Auth-Token')
AUTHN_TOKEN = os.getenv('AUTHN_TOKEN', 'neon-genesis-evangelion')

AUTHZ_HEADER = os.getenv('AUTHZ_HEADER', 'X-Auth-User')
AUTHZ_TOKEN = os.getenv('AUTHZ_TOKEN', 'asuka-langley-soryu')

# 判题机
JUDGE_HOST = os.getenv('JUDGE_HOST', 'localhost')
JUDGE_PORT = os.getenv('JUDGE_PORT', '2358')
USE_HTTPS = os.getenv('JUDGE_SSL', False)
