from logging import config
import os
import re
import requests
from cloud import OSSManager
config_path = r"E:\root\oss\oss-config.json"
md_folder_path = r"E:\temp\agiantii-notebook-local-gitee"

oss_directory = "test-blog/"
oss_manager = OSSManager(config_path=config_path)

pre_url = "https://agiantii-oss-local.oss-cn-hangzhou.aliyuncs.com/"

img_log = []
md_log = []

# debug option

sure_change = True
def save_log():
    with open("img_log.txt", "w") as f:
        for item in img_log:
            f.write("%s\n" % item)
    with open("md_log.txt", "w") as f:
        for item in md_log:
            f.write("%s\n" % item)
def get_suffix(file_path):
    return '.'+file_path.split('.')[-1]
def upload_images_and_update_md(oss_manager:OSSManager, md_folder_path, oss_directory):
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
    
    for root, dirs, files in os.walk(md_folder_path):
        for file in files:
            if file.endswith('.md'):
                has_img = False
                md_file_path = os.path.join(root, file)
                with open(md_file_path, 'r', encoding='utf-8') as md_file:
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
                        oss_image_path = oss_directory + oss_manager.generate_unique_bucket_name()+suffix
                        with open(local_image_path, 'rb') as img_file:
                            oss_manager.upload_file(oss_image_path,img_file.read())
                            print(f"Uploaded {local_image_path} to {pre_url}{oss_image_path}")
                        new_url = pre_url + oss_image_path
                        if(sure_change):updated_content = updated_content.replace(match, new_url)
                    # 如是 http 或 https 开头的图片链接，读取图片内容并上传
                    # elif match.startswith('http'):
                    #     oss_image_path = os.path.join(oss_directory, os.path.relpath(match, md_folder_path).replace(os.sep, '/'))
                    #     oss_manager.upload_file(oss_image_path, requests.get(match).content)
                    #     print(f"Uploaded {match} to {oss_image_path}")
                    #     updated_content = updated_content.replace(match, pre+oss_image_path)
                with open(md_file_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(updated_content)
                if(has_img):
                    md_log.append(md_file_path)

def main():
    
    oss_manager = OSSManager(config_path=config_path)
    # 上传本地 Markdown 文件中的图片并更新路径
    upload_images_and_update_md(oss_manager, md_folder_path, oss_directory)
    save_log()
if __name__ == '__main__':
    main()