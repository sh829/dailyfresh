
from kombu import Exchange, Queue
# celery设置：redis使用情况
# 由本地的redis数据库的1号数据库来传输任务
BROKER_URL = 'redis://127.0.0.1:6379/1'
# 由本地的redis数据库的2号数据库来存储任务返回的参数结果
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'