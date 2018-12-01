from django.conf.urls import url

from apps.goods.views import IndexView,DetailView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index')
    url(r'^goods/(?P<sku_id>\d+)$', DetailView.as_view(),name='detail'),#详情页
]
