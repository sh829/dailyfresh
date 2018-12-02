from django.shortcuts import render,redirect
from django.views import View
from django.core.cache import cache
# Create your views here.
from django_redis import get_redis_connection

from apps.goods.models import GoodsType, IndexGoodsBanner\
    , GoodsSKU, IndexPromotionBanner, IndexTypeGoodsBanner

IndexPromotionBanner, IndexTypeGoodsBanner


class IndexView(View):
    '''首页'''

    def get(self, request):

        '''显示'''
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')  #no pickle
        if context is None:
           # 获取商品分类信息
            print('设置首页缓存')
            types = GoodsType.objects.all()
           # 获取首页轮播商品信息
            indexGoodsBanner = IndexGoodsBanner.objects.all()
           # 获取首页促销活动信息
            indexPromotionBanner = IndexPromotionBanner.objects.all()
           # 获取首页分类商品的展示信息
            for category in types:
                img_banner = IndexTypeGoodsBanner.objects.filter(category=category, display_type=1)
                title_banner = IndexTypeGoodsBanner.objects.filter(category=category, display_type=0)

                #给types对象增加属性img_banner、title_banner
                category.img_banner = img_banner
                category.title_banner = title_banner
            #缓存数据
            context = {
                'types':types,
                'indexGoodsBanner':indexGoodsBanner,
                'indexPromotionBanner':indexPromotionBanner,
                'cart_count':0
            }
            #设置首页缓存
            cache.set('index_page_data',context)
            #判断用户是否登录
        cart_count=0
        if request.user.is_authenticated():
            # 获取redis链接
            conn = get_redis_connection('default')
            print('request.user.id',request.user.id)
            # 拼接key
            cart_key = 'cart_%s'%request.user.id

            #获取用户购物车商品条目数
            #hlen(key)-》返回属性的数目
            cart_count = conn.hlen(cart_key)
        #组织模板上下文
        context.update(cart_count=cart_count)
        #是用模板
        return render(request,'index.html',context)
 # 前端向后端传递数据的三种方式:
    # 1) get传参。
    # 2) post传参。
    # 3）url捕获参数。
    #
    # 前端传递的参数：商品id(sku_id)
    # 商品详情页url地址: '/goods/商品id'

    #  /goods/商品id
class DetailView(View):

    def get(self,request,sku_id):
        '''显示'''
        # 获取商品详细信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reversed('goods:index'))
        # 获取商品分类信息
        types = GoodsType.objects.all()
        # 获取商品评论信息

        # 获取同一SPU的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku_id)
        # 获取同种类新品信息
        new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[0:2]
        # 若用户登录，获取购物车中商品的条目数
        cart_count = 0
        if request.user.is_authenticated:
            # 获取redis链接
            conn = get_redis_connection('default')
            # 拼接key
            key = 'cart_%s'% request.user.id
            # 获取用户购物车中商品的条目数
            # hlen(key) 返回属性的数目
            cart_count = conn.hlen(key)

            # 添加用户的历史浏览记录
            # 拼接key
            history_key = 'history_%s' % request.user.id

            # 先尝试从redis对应列表中移除sku_id
            # lrem(key, count, value) 如果存在就移除，如果不存在什么都不做
            # count = 0 移除所有值为 value 的元素。
            conn.lrem(history_key, 0 ,sku_id)

            # 把sku_id添加到redis对应列表左侧
            # lpush(key, *args)
            conn.lpush(history_key, sku_id)

            #只保存用户最近浏览的5个商品的ID
            conn.ltrim(history_key, 0, 4)

            # 组织模板上下文
        context = {
            'sku':sku,
            'types':types,
            'same_sku_skus':same_spu_skus,
            'new_skus': new_skus,
            'cart_count':cart_count,
        }
        return render(request,'detail.html',context)
class ListView(View):
    pass