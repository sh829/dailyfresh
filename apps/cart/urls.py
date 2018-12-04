from django.conf.urls import url
from apps.cart.views import CartAddView,CartInfoView

urlpatterns = [
    url(r'^add$', CartAddView.as_view(),name='add'),# 购物车添加记录
    url(r'^$', CartInfoView.as_view(), name='show'), #购物车页面展示
]