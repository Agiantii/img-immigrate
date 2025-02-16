from cloud import OSSManager,CloudManager
import os
import re

source_directory = r"E:\temp\anote\algorithm" # 源文件夹 也可以是文件
config_path = r"E:\root\oss\oss-config.json" # 配置文件参考 ./oss-config.json

# analysis 
img_count = 0 # 图片数量
img_size = 0 # 图片大小
# debug options
is_deug =  True

def log(*p, **kwargs):
    if(is_deug):
        print(*p, kwargs)
def error(*p, **kwargs):
    print("error",*p, kwargs)
def debug(*p, **kwargs):
    if(is_deug):
        print(*p, kwargs)
# 复制 old_path 到 new_path
def copy_folder(old_path:str,new_path:str):
    if(os.path.exists(new_path) == False):
        os.makedirs(new_path)
    for path in os.listdir(old_path):
        old_file = os.path.join(old_path,path)
        new_file = os.path.join(new_path,path)
        if(os.path.isdir(old_file)):
            copy_folder(old_file,new_file)
        else:
            with open(old_file, "r", encoding="utf-8") as f:
                content = f.read()
                with open(new_file, "w", encoding="utf-8") as f:
                    f.write(content)

def local_to_cloud(source_path:str,
                   cloudManager:CloudManager,
                   exclude_folder:list[str] = [".git"],
                   cloud_prefix:str="test/",
                   is_remove_local:bool = False):
    """
    @description  : 将本地文件上传到云
    ---------
    @param  : source_path:str : 本地文件路径
    @param  : cloudManager:CloudManager : 云管理器
    @param  : exclude_folder:list[str] : 排除的文件夹
    @param  : cloud_prefix:str : 云文件前缀
        - 注意 如果是 test 传输 则会 test-1.jpg
        - 如果是 test/ 传输 则会 test/1.jpg
    @param  : is_remove_local:bool : 是否删除 上传后的 本地文件
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
                # 拼接 ../test/1.jpg 这种形式
                img_path = os.path.normpath(os.path.join(os.path.dirname(source_path),img_link))
                if(os.path.exists(img_path) == False):
                    error(f"图片不存在: {img_path}")
                with open(img_path, "rb") as img_f:
                    img_content = img_f.read()
                    img_type = os.path.basename(img_path).split('.')[-1]
                try:
                    cloud_path = cloud_prefix+cloudManager.generate_unique_bucket_name()+"."+img_type
                    cloudManager.upload_file(cloud_path,img_content)
                    img_url = cloudManager.get_url()+"/"+cloud_path
                    debug(f"上传成功: {img_url}")
                    new_content = new_content.replace(img_link,img_url)
                    if(is_remove_local):os.remove(img_path)
                except Exception as e:
                    error(e)
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(new_content)        
    # 如果是文件夹
    if(os.path.isdir(source_path)):
        # 如果是排除的文件夹 则不处理
        if(os.path.basename(source_path) in exclude_folder):
            return
        for path in os.listdir(source_path):
            local_to_cloud(os.path.join(source_path,path),cloudManager)
def dirremove(target_directory:str):
    """
    @description  : 删除文件夹
    ---------
    @param  : target_directory:str : 目标文件夹
    """ 
    for path in os.listdir(target_directory):
        target_path = os.path.join(target_directory,path)
        if(os.path.isdir(target_path)):
            dirremove(target_path)
        else:
            os.remove(target_path)
    # os.rmdir(target_directory)
if __name__ == "__main__":
    # # 先清理  target_directory
    # if(os.path.exists(target_directory)):
    #     dirremove(target_directory)
    # shutil.rmtree(target_directory,ignore_errors=True)
    # # 复制
    # shutil.copytree(source_directory,target_directory,dirs_exist_ok=True)
    local_to_cloud(source_path=source_directory,
                   cloudManager=OSSManager(config_path=config_path)
                   )
    print(f"图片数量: {img_count}")
    print(f"图片大小: {img_size/1024}KB")
