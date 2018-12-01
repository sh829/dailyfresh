from django.conf import settings  # 导入settings里设置的163邮箱配置
from django.core.mail import send_mail # 导入django发送邮件函数

from celery_tasks.celery import app as app  # 导入创建的Celery类的对象
# 定义发送邮件任务函数
@app.task
def send_register_active_email(to_email, username, token):
    print("---发送邮件--->",to_email, username, token)
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = """
                       <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
                       请点击一下链接激活您的账号(7小时之内有效)<br/>
                       <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
                   """ % (username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    print('----发送邮件成功----')