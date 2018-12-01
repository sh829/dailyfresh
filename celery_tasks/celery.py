from celery import Celery
# 创建celery实例
app = Celery('celery_tasks')
# celery任务的设置全部来自celeryconfig
app.config_from_object('celery_tasks.celeryconfig')
# 自动搜索任务
app.autodiscover_tasks(['celery_tasks'])