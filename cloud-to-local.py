# from cloud import OSSManager,CloudManager
import re
import requests
import os 
import time
# custom option

source_path = r"E:\blog\ablog-v\docs" # 源文件夹 也可以是文件
target_path:str = "" # 表示就是当前目录可以不用填写
url_include_reg = ["agiantii"]
url_exclude_reg = ["alipay","yuque"]
exclude_folder = [".git"] # 排除的文件夹


# url_include_reg = [re.compile(i) for i  in url_include_reg]
# url_exclude_reg = [re.compile(i) for i in url_exclude_reg]
# exclude_folder = [re.compile(i) for i in exclude_folder]
# analyse 

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
@retry(delay=1,times=3)
def img_get(url):
    return requests.get(url).content
def cloud_to_local(source_path):
    # 如果是 文件
    if(os.path.isfile(source_path)):
        # 且是 md 文件
        if not source_path.endswith(".md"):
            return
        log(source_path)
        with open(source_path,"r",encoding="utf-8") as f:
            md_name = os.path.basename(source_path).split(".")[0]
            md_name = md_name.replace(" ","_")
            content = f.read()
            new_content = content
            img_links_patterns = re.compile(r"!\[.*?\]\((.*?)\)")
            img_links = img_links_patterns.findall(content)
            for img_link in img_links:
                if("http" not in img_link):
                    continue
                # 是否在 include_img_url 里面
                if(not any([i in img_link for i in url_include_reg])):
                    continue
                # 是否 在 exclude_img_url 里面
                if(any([i in img_link for i in url_exclude_reg])):
                    continue
                log(img_link)
                # continue
                # analyse
                global img_count,img_size
                try:
                    res = img_get(img_link)
                    img_size+=len(res)
                    img_count += 1
                    # 放在 md 的 assest/${md_name}文件夹下
                    img_name = img_link.split("/")[-1]
                    img_path = os.path.join(os.path.dirname(source_path),"assets",md_name,img_name)
                    os.makedirs(os.path.join(os.path.dirname(source_path),"assets",md_name),exist_ok=True)
                    with open(img_path,"wb") as f:
                        f.write(res)
                        new_content = new_content.replace(img_link,f"./assets/{md_name}/{img_name}")
                except Exception as e:
                    log(f"error {img_link} {e}")
                    continue
            with open(source_path,"w",encoding="utf-8") as f:
                f.write(new_content)
    else:
        for path in os.listdir(source_path):
            if any([i in path for i in exclude_folder]):
                continue
            cloud_to_local(os.path.join(source_path,path))
                             
if __name__ == "__main__":
    cloud_to_local(source_path)
    print(f"图片数量: {img_count} 图片大小: {img_size/1024/1024}MB")