import os
import re
import requests
import time
from cloud import OSSManager
import  math

# Custom options
remove_old_img = False
is_move_to_new = True
exclude_folder = ["assets", "imgs"]
config_path = r"E:\root\oss\oss-config.json"
old_md_folder_path = r"E:\temp\agiantii-notebook-local-gitee"
target_md_folder_path = r"E:\temp\anote"
oss_directory = "anote/"
oss_manager = OSSManager(config_path=config_path)
pre_url = oss_manager.get_url() + "/"

if(not is_move_to_new):
    target_md_folder_path = old_md_folder_path

img_url_pattern = re.compile(r".*yuque.*")
img_log = []
md_log = []

# Debug options
sure_change = True
is_debug = False
file_size = 0

# use debug function to print
def debug(*args):
    if is_debug:
        print(*args)
def debug_i(*args):
    print(*args)
def debug_error(*args):
    print(*args)
# Clock decorator to measure execution time
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
    return '.' + file_path.split('.')[-1]

def get_url_file_type(url):
    # common image types
    common_type = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'pdf', 'tiff', 'svg', 'ico']
    for t in common_type:
        if t in url:
            return t
    return None

def upload_images_and_update_md(oss_manager: OSSManager, md_folder_path, oss_directory):
    global file_size
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
                    debug(f"Found image: {match}")
                    suffix = get_suffix(match)
                    has_img = True
                    local_image_path = os.path.normpath(os.path.join(root, match))
                    img_log.append(local_image_path)
                    if os.path.exists(local_image_path):
                        oss_image_path = oss_directory + oss_manager.generate_unique_bucket_name() + suffix
                        with open(local_image_path, 'rb') as img_file:
                            oss_manager.upload_file(oss_image_path, img_file.read())
                            file_size += os.path.getsize(local_image_path)
                            debug(f"Uploaded {local_image_path} to {pre_url}{oss_image_path}")
                        new_url = pre_url + oss_image_path
                        if sure_change:
                            updated_content = updated_content.replace(match, new_url)
                    # if match is a url
                    elif img_url_pattern.match(match):
                        # debug_i(match)
                        try:
                            response = requests.get(match)
                            if response.status_code == 200:
                                suffix = get_url_file_type(match)
                                oss_image_path = oss_directory + oss_manager.generate_unique_bucket_name() + '.' + suffix
                                oss_manager.upload_file(oss_image_path, response.content)
                                file_size += len(response.content)
                                debug(f"Uploaded {match} to {pre_url}{oss_image_path}")
                                new_url = pre_url + oss_image_path
                                if sure_change:
                                    updated_content = updated_content.replace(match, new_url)
                        except Exception as e:
                            debug(f"Failed to download {match}: {e}")
                for match in obsidian_image_pattern.findall(content):
                    debug(f"Found image: {match}")
                    suffix = get_suffix(match)
                    has_img = True
                    local_image_path = os.path.normpath(os.path.join(root, match))
                    img_log.append(local_image_path)
                    if os.path.exists(local_image_path):
                        oss_image_path = oss_directory + oss_manager.generate_unique_bucket_name() + suffix
                        with open(local_image_path, 'rb') as img_file:
                            oss_manager.upload_file(oss_image_path, img_file.read())
                            file_size += os.path.getsize(local_image_path)
                        new_url = pre_url + oss_image_path
                        if sure_change:
                            updated_content = updated_content.replace(match, new_url)
                
                # Move file to new directory if required
                if is_move_to_new:
                    relative_path = os.path.relpath(file_path, start=old_md_folder_path)
                    new_md_file_path = os.path.join(target_md_folder_path, relative_path)
                else:
                    new_md_file_path = file_path
                
                os.makedirs(os.path.dirname(new_md_file_path), exist_ok=True)
                with open(new_md_file_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(updated_content)
                if has_img:
                    md_log.append(new_md_file_path)
            else:
                # Directly copy non-markdown files
                relative_path = os.path.relpath(os.path.join(root, file), start=old_md_folder_path)
                new_file_path = os.path.join(target_md_folder_path, relative_path)
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                with open(new_file_path, 'wb') as f:
                    with open(os.path.join(root, file), 'rb') as f2:
                        f.write(f2.read())
                    
def clear_md_end_with_now(target_folder):
    for root, _, files in os.walk(target_folder):
        for file in files:
            if file.endswith('_now.md'):
                print(file)
                file_path = os.path.join(root, file)
                os.remove(file_path)

def replace_obsidian_path(target_folder):
    for root, _, files in os.walk(target_folder):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                print(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    new_content = re.sub(r"!\[\[(.*?)\]\]", r"![alt](\1)", content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

#
def retry(times, delay):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Failed to download {args[0]}: {e}")
                    time.sleep(delay)
                    pass
        return wrapper
    return decorator
@retry(times = 3 , delay = 2)
def get_res(url):
    return requests.get(url)
def cloud_to_cloud(folder_path):
    link_pattern = re.compile(r"!\[.*?\]\((.*?)\)")
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for match in link_pattern.findall(content):
                        if(img_url_pattern.match(match)):
                            print(match)
                            suffix = get_url_file_type(match)
                            if(suffix == None):
                                debug_error(f"Unknown suffix: {match}")
                                continue
                            try:
                                response = get_res(match)
                                if response != None:
                                    oss_image_path = oss_directory + oss_manager.generate_unique_bucket_name() + '.' + suffix
                                    oss_manager.upload_file(oss_image_path, response.content)
                                    file_size += len(response.content)
                                    print(f"Uploaded {match} to {pre_url}{oss_image_path}")
                                    new_url = pre_url + oss_image_path
                                    content = content.replace(match, new_url)
                            except Exception as e:
                                print(f"Failed to download {match}: {e}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                    
@clock
def main():
    oss_manager = OSSManager(config_path=config_path)
    # print(oss_manager.get_url())
    # 上传本地 Markdown 文件中的图片并更新路径
    upload_images_and_update_md(oss_manager, old_md_folder_path, oss_directory)

    
    clear_md_end_with_now(target_md_folder_path)
    replace_obsidian_path(target_md_folder_path)
    cloud_to_cloud(target_md_folder_path)
    if is_debug:
        save_log()
    # 根据 file_size 计算文件大小 大于 1MB 的文件 用 MB 为单位
    if file_size > 1024 * 1024:
        print(f"Total file size: {math.ceil(file_size / 1024 / 1024)} MB")
    else:
        print(f"Total file size: {math.ceil(file_size / 1024)} KB")


if __name__ == '__main__':
    main()