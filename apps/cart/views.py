from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
# Create your views here.
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU


class CartAddView(View):
    '''购物车记录添加'''
    def post(self,requst):
        # 判断用户是否登录
        user = requst.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'message': '请先登录'})
        '''获取用户传递的参数'''
        sku_id = requst.POST.get('sku_id')
        count = requst.POST.get('count')
        # 参数校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 0,  'message': '参数不完整'})
        # 检验商品ID
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'message': '商品信息错误'})
        # 检验商品数量
        try:
            count=int(count)
        except Exception as e:
            return JsonResponse({'res': 3, 'message': '商品数量必须为数字'})
        # 业务处理，购物车记录添加
        # 获取redis链接
        conn = get_redis_connection('default')
        # 拼接key
        key = 'cart_%d'% user.id
        # hget(key, field)
        cart_count = conn.hget(key, sku_id)

        if cart_count:
            # 如果用户购物车已经添加过sku_id商品，购物车对应商品的数目需要累加
            count+=int(cart_count)
        # 检验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'message': '商品库存不足'})
        # 设置用户购物车中sku_id商品和数量
        # hset(key,field,value) 存在就修改，不存在就新增
        conn.hset(key,sku_id,count)
        # 获取用户购物车中商品的条目数
        cart_count = conn.hlen(key)
        # 返回应答
        return JsonResponse({'res': 5, 'cart_count': cart_count,'errmsg':'添加购物车成功'})

class CartInfoView(View):
    '''购物车页面展示'''
    def get(self,request):
        # 获取当前登录用户
        user = request.user
        # 从redis获取用户购物车数据
        conn = get_redis_connection('default')
        # 拼接key
        key = 'cart_%d'% user.id
        # hgetall(key),返回的是一个字典，键是商品ID，值是商品数量
        cart_dict = conn.hgetall(key)
        total_count = 0
        total_amount = 0
        #遍历获取购物车商品详细信息
        skus=[]
        for sku_id, count in cart_dict.items():
            # 根据sku_id取商品
            sku = GoodsSKU.objects.get(id=sku_id)
            # 计算商品小计
            amount = sku.price * int(count)
            # 给sku增加属性amount和count,分别保存用户购物车商品的小计和数量
            sku.amount = amount
            sku.count = count
            # 追加商品信息
            skus.append(sku)
            #累计计算用户购物车中商品总价格和总数量
            total_count += int(count)
            total_amount += amount
        # 组织模板上下文
        context={
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
        }
        return render(request, 'cart.html', context)

