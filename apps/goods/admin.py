from django.contrib import admin
from apps.goods.models import Goods,GoodsType,GoodsSKU,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner,GoodsImage
from django.core.cache import cache
# Register your models here.

class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新时候调用'''
        # 调用ModelAdmin中的save_model方法实现
        super().save_model(request, obj, form, change)

        # 附加操作1：发出生成静态首页的任务

        # 附加操作2,：清除首页缓存
        cache.delete('index_page_data')
    
    def delete_model(self, request, obj):
        '''删除数据时调用'''
        super().delete_model(request, obj)
        # 附加操作: 清除首页缓存
        cache.delete('index_page_data')

class GoodsTypeAdmin(BaseModelAdmin):
    """商品种类模型admin管理类"""
    list_display = ('name','logo')

class GoodsSKUInfo(admin.StackedInline):
    model = GoodsSKU
    extra = 1

class GoodsAdmin(BaseModelAdmin):
    inlines = [GoodsSKUInfo]
    """商品种类模型admin管理类"""
    list_display = ('name',)

class GoodsSKUAdmin(BaseModelAdmin):
    """商品种类模型admin管理类"""
    search_fields=('name', 'unite','price','stock','sales')
    list_display = ('name', 'unite', 'price', 'stock', 'sales')

class GoodsImageAdmin(BaseModelAdmin):
    '''商品图片'''
    pass

class IndexGoodsBannerAdmin(BaseModelAdmin):
    """首页轮播商品模型admin管理类"""
    list_display = ('sku','index')


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    list_filter = ('category','display_type')
    """首页分类商品展示模型admi管理类"""
    list_display = ('category','sku','display_type','index')


class IndexPromotionBannerAdmin(BaseModelAdmin):
    """首页促销活动admin管理类"""
    list_display = ('name','url','index')

admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsImage,GoodsImageAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
