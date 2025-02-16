from logging import root
import os
import re
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
def main():
    target_folder = r"E:\temp\new-anote"
    replace_obsdian_path(target_folder)

main()