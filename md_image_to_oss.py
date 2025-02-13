import math
import os
import re
import requests
from cloud import OSSManager

# custom_option
remove_old_img = False
is_move_to_new = True
 # exclude folder to immigrate
exclude_folder = ["assets","imgs"]
config_path = r"E:\root\oss\oss-config.json"
old_md_folder_path = r"E:\temp\agiantii-notebook-local-gitee"
tart_md_folder_path = r"E:\temp\new-anote"

oss_directory = "test-blog/"
oss_manager = OSSManager(config_path=config_path)

pre_url = oss_manager.get_url()+"/"

img_log = []
md_log = []

# debug option

sure_change = True
is_debug = True
file_size = 0

# clock decorator
import time
def clock(func):
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        name = func.__name__
        print(f"{name} elapsed time: {elapsed}")
        return result
    return clocked
def save_log():
    with open("img_log.txt", "w") as f:
        for item in img_log:
            try:
                f.write("%s\n" % item)
            except:
                print(item)
    with open("md_log.txt", "w") as f:
        for item in md_log:
            try:
                f.write("%s\n" % item)
            except:
                print(item)
def get_suffix(file_path):
    return '.'+file_path.split('.')[-1]
def get_url_file_type(url):
    common_type = ['jpg','jpeg','png','gif','bmp','webp']
    for t in common_type:
        if t in url:
            return t
def upload_images_and_update_md(oss_manager:OSSManager, md_folder_path, oss_directory):
    global  file_size
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
    obsidian_image_pattern = re.compile(r'!\[\[(.*?)\]\]')
    for root, dirs, files in os.walk(md_folder_path):
        if any(exclude in root for exclude in exclude_folder):
            continue
        for file in files:
            if file.endswith('.md'):
                has_img = False
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as md_file:
                    content = md_file.read()
                
                updated_content = content
                for match in image_pattern.findall(content):
                    print(f"Found image: {match}")
                    suffix = get_suffix(match)
                    # print(match,suffix)
                    has_img = True
                    local_image_path = os.path.normpath(os.path.join(root, match))
                    img_log.append(local_image_path)
                    # continue
                    if os.path.exists(local_image_path):
                        oss_image_path = oss_directory + oss_manager.generate_unique_bucket_name() + suffix
                        with open(local_image_path, 'rb') as img_file:
                            oss_manager.upload_file(oss_image_path, img_file.read())
                            file_size += os.path.getsize(local_image_path)
                            print(f"Uploaded {local_image_path} to {pre_url}{oss_image_path}")
                        new_url = pre_url + oss_image_path
                        if sure_change:
                            updated_content = updated_content.replace(match, new_url)

                for match in obsidian_image_pattern.findall(content):
                    print(f"Found image: {match}")
                    suffix = get_suffix(match)
                    # print(match,suffix)
                    has_img = True
                    local_image_path = os.path.normpath(os.path.join(root, match))
                    img_log.append(local_image_path)
                    # continue
                    if os.path.exists(local_image_path):
                        oss_image_path = oss_directory + oss_manager.generate_unique_bucket_name()+suffix
                        with open(local_image_path, 'rb') as img_file:
                            oss_manager.upload_file(oss_image_path,img_file.read())
                            file_size += os.path.getsize(local_image_path)
                            print(f"Uploaded {local_image_path} to {pre_url}{oss_image_path}")
                        new_url = pre_url + oss_image_path
                        if(sure_change):updated_content = updated_content.replace(match, new_url)
                # 如要移动文件到新目录
                if(is_move_to_new):
                    relative_path = os.path.relpath(file_path, start=old_md_folder_path)
                    new_md_file_path = os.path.join(tart_md_folder_path, relative_path)
                # 是否迁移到新目录
                final_markdown_file_path = new_md_file_path if is_move_to_new else file_path
                os.makedirs(os.path.dirname(final_markdown_file_path), exist_ok=True)
                with open(final_markdown_file_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(updated_content)
                if(has_img):
                    md_log.append(final_markdown_file_path)
            else:
                # 直接复制文件
                relative_path = os.path.relpath(os.path.join(root, file), start=old_md_folder_path)
                file_path = os.path.join(tart_md_folder_path, relative_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    with open(os.path.join(root, file), 'rb') as f2:
                        f.write(f2.read())
def clear_md_end_with_now(target_folder):
    for root,_,files in os.walk(target_folder):
        for file in files:
            if(file.endswith('_now.md')):
                print(file)
                file_path = os.path.join(root,file)
                os.remove(file_path) 
def replace_obsdian_path(target_folder):
    for root,_,files in os.walk(target_folder):
        for file in files:
            if(file.endswith('.md')):
                file_path = os.path.join(root,file)
                obsidian_pattern = re.compile("!\[\]")   
                print(file_path)
                with open(file_path,'r',encoding='utf-8') as f:
                    content = f.read()
                    new_content =  re.sub(r"!\[\[(.*?)\]\]",r"![alt](\1)",content)
                    with open(file_path,'w',encoding='utf-8') as f:
                        f.write(new_content)       

        
@clock
def main():
    oss_manager = OSSManager(config_path=config_path)
    print(oss_manager.get_url())    
    oss_manager = OSSManager(config_path=config_path)
    # 上传本地 Markdown 文件中的图片并更新路径
    upload_images_and_update_md(oss_manager, old_md_folder_path, oss_directory)
    clear_md_end_with_now(tart_md_folder_path)
    replace_obsdian_path(tart_md_folder_path)
    if(is_debug):
        save_log()
        # 
    print(f"Total size: {file_size} bytes")
    print(f"Total size: {file_size/1024} KB")
    print(f"Total size: {file_size/1024/1024} MB")
if __name__ == '__main__':
    main()