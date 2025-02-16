from urllib import response
from cloud import OSSManager,CloudManager
import re
import requests
import os 
import time
from atool import get_url_file_type
import cloud
# custom option

source_path = r"E:\temp\new-anote\algorithm" # 源文件夹 也可以是文件
target_path:str = "" # 表示就是当前目录可以不用填写
exclude_folder = [".git"] # 排除的不要处理的文件夹

img_count = 0
img_success_count = 0
img_size = 0
# debug option
is_log = True # 是否打印日志

def log(*args):
    if is_log:
        print(*args)
def retry(delay=1, times=3):
    def wrapper(func):
        def inner(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f" 可能请求过于频繁retry {i} times")
                    time.sleep(delay)
            return func(*args, **kwargs)
        return inner
    return wrapper
def cloud_to_cloud(source_path:str,
                   cloudManager:CloudManager,
                   cloud_prefix:str="test1/",
                   exclude_folder:list[str] = [".git"]
                   ):
    
    """
    @description  : 将一个 图床 迁移到 另一个图床 会改变原文件
    ---------
    @param  : source_path:str : 本地文件路径 可以是文件夹 也 可以是文件 
    @param  : cloudManager:CloudManager : 云管理器
    @param  : exclude_folder:list[str] : 排除的文件夹
    """
    # 如果是 md文件
    if(os.path.isfile(source_path)):
        if(source_path.endswith('.md') != True):
            return 
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()
            new_content = content
            img_patterns = re.compile(r"!\[.*?\]\((.*?)\)") # 匹配图片链接
            img_links =  img_patterns.findall(content)
            for img_link in img_links:
                # 判断是否为网络图片
                if(not ("http" in img_link)):
                    continue
                # 不要重复上传到自己的云
                if(cloudManager.get_url() in img_link):
                    continue
                upload_img_url = cloud_prefix+cloudManager.generate_unique_bucket_name()+"."+get_url_file_type(url=img_link)
                try:
                    img_content = requests.get(img_link)
                    cloudManager.upload_file(upload_img_url,img_content)
                    img_url = cloudManager.get_url()+"/"+upload_img_url
                    log(img_url)
                    new_content = content.replace(img_link,img_url)
                except Exception as e:
                    log(e)
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(new_content)
    else:
        # 处理文件夹
        # 如果是排除的文件夹 则不处理
        for path in os.listdir(source_path):
            if(os.path.basename(source_path) in exclude_folder):
                return
            cloud_to_cloud(os.path.join(source_path,path),cloudManager) 
if __name__ == "__main__":
    cloud_to_cloud(source_path=source_path,cloudManager=OSSManager(config_path=r"E:\root\oss\oss-config.json"))