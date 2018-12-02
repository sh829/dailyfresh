from django.test import TestCase
import requests
from celery_tasks import tasks
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
# Create your tests here.
# thinkpad modify
# xiaomi modify
class usercase(TestCase):
    def testSendEmail(self):
        info = {'confirm': "123456"}
        serializer = Serializer(settings.SECRET_KEY, 3600 * 7)
        # 返回bytes类型
        token = serializer.dumps(info)
        print(token)
        # str
        token = token.decode()
        print(token)
        # 发送邮件
        tasks.send_register_active_email("243237408@qq.com", "username", token)

