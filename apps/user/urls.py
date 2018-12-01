from django.conf.urls import url
from apps.user.views import RegisterView, ActiveView, LoginView\
    , AddressView, LogoutView, UserOrderView,UserInfoView

urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name='register'),  # 注册
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 激活
    url(r'^login', LoginView.as_view(), name='login'),  #登录
    url(r'^logout', LogoutView.as_view(), name='logout'), #注销
    url(r'^address$', AddressView.as_view(), name='address'), #地址
    url(r'^order/(?P<page>(/d)*)$', UserOrderView.as_view(),name='order'),#订单信息
    url(r'^$', UserInfoView.as_view(), name='user'),  # 用户中心-信息页
]
