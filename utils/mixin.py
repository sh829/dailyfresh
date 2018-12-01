"""继承View来复写as_view方法"""

from django.views.generic import View
from django.contrib.auth.decorators import login_required

class LoginRequiredView(View):
    @classmethod
    def as_view(cls, **initkwargs):
        '''调用View类中的as_view'''
        view = super().as_view(**initkwargs)
        # 调用login_required装饰器函数
        return login_required(view)

class LoginRequireMixin(View):
    @classmethod
    def as_view(cls, **initkwargs):
        # 使用super调用as_view
        view = super().as_view(*initkwargs)

        #调用login_required装饰器函数
        return login_required(view)