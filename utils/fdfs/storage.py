"""自定义上传存储文件类、连接FDFS"""
from django.core.files.storage import Storage # 自定义存储类需继承于Storage
from django.conf import settings # 导入settings用于获取设置的一些配置参数
from fdfs_client.client import Fdfs_client
import os.path


class FDFSStorage(Storage):
    """fast DFS文件存储类"""
    def __init__(self,clinet_conf=None, nginx_url=None):
        '''初始化'''
        if clinet_conf is None:
            clinet_conf = settings.FDFS_CLIENT_CONF #指向'utils/fdfs/client.conf'
        self.client_conf = clinet_conf

        if nginx_url is None:
            nginx_url=settings.FDFS_NGINX_URL # 指向Nginx服务地址
        self.nginx_url=nginx_url

    def open(self, name, mode='rb'):
        '''用不到打开，所以省略'''
        pass
    def _save(self, name, content):
        '''保存文件时使用'''
        # name 上传文件的名称 a.txt
        # content file文件对象，包含了上传文件的内容
        print('运行到上传到文件系统前',content)
        #上传文件到fdfs文件系统
        client = Fdfs_client(self.client_conf)
        # 获取上传文件的内容
        file_content = content.read()
        #文件后缀名
        file_ext_name=os.path.splitext(name)[1]       
        file_ext_name=file_ext_name[1:]
        print('后缀名是',file_ext_name)
        # 上传文件
        response = client.upload_by_buffer(file_content, file_ext_name)
        #response = client.upload_by_filename(name)
        if response is None or response.get('Status') != 'Upload successed.':
            #上传失败
            raise Exception('上传文件到fdfs系统失败')
        # 获取保存文件ID
        file_id = response.get('Remote file_id')
        print('运行到上传到文件系统成功，file_id是', file_id)
        # 返回file_id
        return file_id
    def exists(self,name):
        '''判断文件是否存在'''
        return False
    def url(self, name):
        '''返回可访问文件的url地址，此地址在模板中可以通过sku.image.url进行获取'''
        return self.nginx_url + name
