from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.generic import View
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
import re

from apps.goods.models import GoodsSKU
from apps.order.models import OrderInfo, OrderGoods
from apps.user.models import User, Address
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.contrib.auth.hashers import check_password
# django内置的认证系统函数
from django.contrib.auth import authenticate, login, logout
# django认证中的用户登入检测
from django.contrib.auth.decorators import login_required
from celery_tasks import tasks
# Create your views here.
# /user/register

class RegisterView(View):
    '''注册'''
    def get(self, request):
        '''显示'''
        print("----get-----")
        return render(request, 'register.html')

    def post(self,request):
        '''注册处理'''
        # 1.接受参数
        username = request.POST.get('user_name', None)  #None
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        # 2.参数校验（后端校验）
        # 验证数据的完整性
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '参数不完整'})
        # 验证邮箱格式
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        # 验证用户名是否已注册

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user is not None:
            return render(request, 'register.html', {'errmsg': '用户名已注册'})
        # 验证邮箱是否已注册
        '''
            try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            User=None
        if user is not None:
            return render(request, 'register.html', {'errmsg': '邮箱已注册'})
        '''
        # 3.注册信息存入用户信息表
        user = User.objects.create_user(username, email, password)
        user.is_active = 0  #用户注册完还没激活，即默认激活状态为0，待激活为1
        user.save()
        # 4.发送注册确认邮件
        '''
        直接在post视图处理中发送邮件——逻辑清晰，但是只有邮件发送后才会执行后面
        的调整首页操作，用户可能需要等待。交给其他进程来进行处理——
        像发邮件这种耗时操作交给其他进行来处理，而视图函数直接执行跳转，
        用户不等待，提高用户体验。
        '''
        # 注册之后，需要给用户的注册邮箱发送激活邮件，在激活邮件中需要包含激活链接
        # 激活链接: /user/active/用户id
        # 存在问题: 其他用户恶意请求网站进行用户激活操作
        # 解决问题: 对用户的信息进行加密，把加密后的信息放在激活链接中，激活的时候在进行解密
        # /user/active/加密后token信息
        # 对用户的身份信息进行加密，生成激活token信息
        serializer = Serializer(settings.SECRET_KEY, 3600 * 7)
        info = {'confirm': user.id}
        # 返回bytes类型
        token = serializer.dumps(info)
        # str
        token = token.decode()
        print('发送邮件', email, username, token)
        # 发送邮件
        tasks.send_register_active_email.delay(email, username, token)
        print('跳转到首页')
        # 返回应答: 跳转到首页
        return redirect('user:login')

class ActiveView(View):
    '''激活'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600*7)
        # 获取待激活用户id
        try:

            info = serializer.loads(token)
            user_id = info['confirm']
            # 激活用户
            user = User.objects.get(id=user_id)
            print('激活邮件', info,user)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已失效
            # 实际开发: 返回页面，让用户点击链接再发激活邮件
            return HttpResponse('激活链接已失效')

class LoginView(View):
    '''登录'''
    def  get(self, request):
        # 判断用户是否记住用户名
        username = request.COOKIES.get("username")
        checked = "checked"
        if username is None:
            username = ""
            checked = ""
        return render(request, "login.html", {"username": username, "checked": checked})

    def post(self, request):
        """登录校验"""
        # 1.接收参数
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')
        print(username,password,remember)
        # 2.参数校验
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '参数不完整'})
        # 3.业务处理：登录校验
        #user = authenticate(username=username, pwd=password)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'login.html', {'errmsg': '用户名不存在'})
        pwd=user.password
        if check_password(password,pwd):
        #if user is not None:
            # 用户名密码都正确
            if user.is_active:
                # 用户已激活
                # 记住用户的登录状态
                login(request, user)
                # 获取用户登录之前访问的url地址，默认跳转到 首页
                next_url = request.GET.get('next', reverse('user:address'))  # None
                print(next_url)
                # 跳转到next_url
                response = redirect(next_url)
                if remember == 'on':
                    # 设置cookie username
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '用户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': "用户名或密码错误"})

class LogoutView(View):
    """退出"""
    def get(self, request):
    # 清除用户登录状态,内置的logout函数会自动清除当前session
        logout(request)
        # 跳转到登录
        return redirect(reverse('user:login'))

from utils.mixin import LoginRequireMixin
from django_redis import get_redis_connection
class UserInfoView(LoginRequireMixin, View):
    """用户中心-信息页"""
    def get(self, request):
        '''显示'''
        # 获取当前登录用户
        user = request.user
        # 根据当前登录用户获取默认收货地址
        address = Address.objects.get_default_address(user)
        # 获取用户最近的浏览信息
        # 若采用redis第三包交互时
        # from redis import StrictRedis
        # conn = StrictRedis(host='172.16.179.142', port=6379, db=5)
        # 返回StrictRedis类的对象
        # 若采用django-redis包时
        conn = get_redis_connection('default')
        # 拼接key
        history_key = 'history_%d' % user.id
        # lrange(key, start, stop) 返回是列表
        # 获取用户最新浏览的5个商品的id
        sku_ids = conn.lrange(history_key, 0, 4) #[1, 3, 5, 2]

        skus = []
        for sku in sku_ids:
            # 根据商品的id查询商品的信息
            sku =GoodsSKU.objects.get(id=sku_ids)
            skus.append(sku)
        # 组织模板上下文
        context = {
            'address': address,
            'skus': skus,
            'page': 'user'
        }
        return render(request, 'user_center_site.html',context)
class AddressView(LoginRequiredMixin,View):
    '''用户中心，地址也'''
    def get(self, request):
        user =request.user
        default_address = Address.objects.get_default_address(user)
        all_address = Address.objects.get_all_address(user)
        # 组织模板上下文
        context = {
            'address': default_address,
            'all_address':all_address,
            'page':'address'
        }
        return render(request,'user_center_site.html',context)

    def post(self,request):
        '''地址添加'''
        # 接收参数
        receiver = request.POST.get('receiver')
        addr = request.POST.get('direction')
        mail =request.POST.get('mail_code')
        phone = request.POST.get('phone_number')
        is_default = request.POST.get('is_default')
        # 校验手机号
        # 参数校验
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 业务处理：添加收货地址
        # 如果用户已经有默认地址，新添加的地址作为非默认地址，否则作为默认地址
        # 获取登录用户user
        user = request.user
        address = Address.objects.get_default_address(user)
        # is_default = True
        # if address is not None:
        #     is_default = False
        # 添加收货地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=mail,
                               is_default=is_default
                               )
        # 返回应答，刷新地址页面
        return redirect(reverse('user:address'))

class UserOrderView(LoginRequiredMixin, View):
    '''用户中心，全部订单'''
    def get(self,request, page):
        # 获取登录用户
        user = request.user
        # 查询所有订单
        info_msg = 1 #若有订单则为1
        try:
            order_infos = OrderInfo.objects.filter(user=user).order_by('-create_time')
        except OrderInfo.DoesNotExist:
            info_msg = 0
        context = {
            'page':'order',
            'info_msg':info_msg,
        }
        if info_msg==1:
            for order_info in order_infos:
                order_goods = OrderGoods.objects.filter(order=order_info)
                for order_good in order_goods:
                    #商品小计
                    amount = order_good.price * order_good.count
                    order_good.amount = amount
                order_info.order_goods = order_goods
                order_info.status_title = OrderInfo.ORDER_STATUS[order_info.order_status]

            #分页操作
            from django.core.paginator import Paginator
            paginator = Paginator(order_infos, 3)
            #处理页码
            page = int(page)
            if page >paginator.num_pages:
                # 默认获取第一页的内容
                page = 1
            # 获取第page页的内容，返回Page类的实例
            order_infos_page = paginator.page(page)
            # 页码处理
            # 如果分页之后页码超过5页，最多在页面上只显示5个页码：当前页前2页，当前页，当前页后2页
            # 1) 分页页码小于5页，显示全部页码
            # 2）当前页属于1-3页，显示1-5页
            # 3) 当前页属于后3页，显示后5页
            # 4) 其他请求，显示当前页前2页，当前页，当前页后2页
            num_page = paginator.num_pages #总页数
            if num_page < 5:
                pages = range(1, num_page+1)
            elif page<3:
                pages = range(1,6)
            elif num_page - page <=2:
                pages = range(num_page-4, num_page+1)
            else:
                pages = range(page-2, page+3)

            context = {
                'page':'order',
                'order_infos':order_infos,
                'info_msg':info_msg,
                'pages':pages,
                'order_info_page':order_infos_page
            }
            return render(request,'user_center_info.html',context)
